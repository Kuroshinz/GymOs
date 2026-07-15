import 'package:flutter/material.dart';
import '../../../core/network/api_client.dart';
import '../../dashboard/domain/gymos_state_model.dart';
import '../domain/workout_log_models.dart';

class WorkoutPage extends StatefulWidget {
  const WorkoutPage({super.key});

  @override
  State<WorkoutPage> createState() => _WorkoutPageState();
}

class _WorkoutPageState extends State<WorkoutPage> {
  final ApiClient _apiClient = ApiClient();
  GymAppState? _appState;
  List<ExerciseLog> _exerciseLogs = [];
  bool _isLoading = true;
  String _message = '';
  late DateTime _startTime;

  @override
  void initState() {
    super.initState();
    _startTime = DateTime.now();
    _loadState();
  }

  Future<void> _loadState() async {
    setState(() {
      _isLoading = true;
    });
    try {
      final state = await _apiClient.fetchUnifiedDashboardState();
      
      // Map suggested exercise from workout_recommender dynamically
      final String suggested = state.workoutRecommender.suggestedExercise;
      final String suggestedId = suggested.toLowerCase().replaceAll(' ', '_');

      setState(() {
        _appState = state;
        _exerciseLogs = [
          ExerciseLog(
            exerciseId: suggestedId,
            exerciseName: suggested,
            sets: List.generate(3, (index) => SetLog(
              setNumber: index + 1,
              weight: 0.0,
              reps: 0,
              rir: 2,
              isCompleted: false,
            )),
          ),
          ExerciseLog(
            exerciseId: 'chest_supported_row',
            exerciseName: 'Chest Supported Row',
            sets: List.generate(3, (index) => SetLog(
              setNumber: index + 1,
              weight: 0.0,
              reps: 0,
              rir: 2,
              isCompleted: false,
            )),
          ),
          ExerciseLog(
            exerciseId: 'seated_cable_row',
            exerciseName: 'Seated Cable Row',
            sets: List.generate(2, (index) => SetLog(
              setNumber: index + 1,
              weight: 0.0,
              reps: 0,
              rir: 2,
              isCompleted: false,
            )),
          ),
        ];
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
        _message = 'Offline mode active';
      });
    }
  }

  Future<void> _finishSession() async {
    int completedCount = 0;
    for (var ex in _exerciseLogs) {
      for (var s in ex.sets) {
        if (s.isCompleted && s.weight > 0 && s.reps > 0) {
          completedCount++;
        }
      }
    }

    if (completedCount == 0) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please check and complete at least one set with weight and reps before finishing.'),
          backgroundColor: Color(0xFFEF4444),
        ),
      );
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      final session = WorkoutSessionLog(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        programId: 'ppl-ul',
        startTime: _startTime,
        endTime: DateTime.now(),
        exercises: _exerciseLogs,
      );

      final success = await _apiClient.saveWorkoutSession(session);
      if (!mounted) return;
      if (success) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Hypertrophy volume logged successfully! ($completedCount sets synced)'),
            backgroundColor: const Color(0xFF10B981),
          ),
        );
        Navigator.of(context).pop();
      } else {
        throw Exception('Server rejected the session');
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to save workout: $e'),
          backgroundColor: const Color(0xFFEF4444),
        ),
      );
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Widget _buildMuscleFatigueHeader() {
    if (_appState == null) return const SizedBox();
    return Container(
      padding: const EdgeInsets.all(16),
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: const Color(0xFF121324),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFF1F2035)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Target Muscle Status', style: TextStyle(color: Colors.grey, fontSize: 13, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: _appState!.muscleStatus.entries.map((entry) {
              final muscle = entry.key;
              final status = entry.value;
              return Column(
                children: [
                  Text(muscle, style: const TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 6),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: status.color.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(6),
                      border: Border.all(color: status.color.withValues(alpha: 0.3)),
                    ),
                    child: Text(
                      '${status.statusText} (${status.fatigue.toInt()}%)',
                      style: TextStyle(color: status.color, fontSize: 11, fontWeight: FontWeight.bold),
                    ),
                  ),
                ],
              );
            }).toList(),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final titleText = _appState?.activeProgramName ?? 'Workout - PULL';

    return Scaffold(
      backgroundColor: const Color(0xFF070814),
      appBar: AppBar(
        title: Text(titleText, style: const TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFF121324),
        actions: [
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16.0),
            child: Center(
              child: Text(
                _message,
                style: const TextStyle(color: Color(0xFF6366F1), fontSize: 12),
              ),
            ),
          )
        ],
      ),
      body: _isLoading
          ? ListView.builder(
              padding: const EdgeInsets.all(16.0),
              itemCount: 4,
              itemBuilder: (context, index) {
                return Card(
                  color: const Color(0xFF121324),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  margin: const EdgeInsets.only(bottom: 16),
                  child: const Padding(
                    padding: EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            SkeletonLoader(width: 150, height: 20),
                            SkeletonLoader(width: 60, height: 24),
                          ],
                        ),
                        SizedBox(height: 16),
                        SkeletonLoader(width: double.infinity, height: 38),
                        SizedBox(height: 8),
                        SkeletonLoader(width: double.infinity, height: 38),
                        SizedBox(height: 8),
                        SkeletonLoader(width: double.infinity, height: 38),
                      ],
                    ),
                  ),
                );
              },
            )
          : ListView(
              padding: const EdgeInsets.all(16.0),
              children: [
                _buildMuscleFatigueHeader(),
                ...List.generate(_exerciseLogs.length, (index) {
                  final exercise = _exerciseLogs[index];
                  return Card(
                    color: const Color(0xFF121324),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                    margin: const EdgeInsets.only(bottom: 16),
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Expanded(
                                child: Text(
                                  exercise.exerciseName,
                                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white),
                                ),
                              ),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                decoration: BoxDecoration(
                                  color: const Color(0xFF6366F1).withValues(alpha: 0.1),
                                  borderRadius: BorderRadius.circular(8),
                                  border: Border.all(color: const Color(0xFF6366F1).withValues(alpha: 0.3)),
                                ),
                                child: Text(
                                  _appState?.workoutRecommender.aiCoachedTarget ?? '3 sets x 10 reps',
                                  style: const TextStyle(color: Color(0xFF6366F1), fontSize: 12, fontWeight: FontWeight.bold),
                                ),
                              )
                            ],
                          ),
                          const SizedBox(height: 16),
                          ...List.generate(exercise.sets.length, (setIdx) {
                            final currentSet = exercise.sets[setIdx];
                            return Padding(
                              padding: const EdgeInsets.only(bottom: 8.0),
                              child: WorkoutSetRow(
                                setLog: currentSet,
                                onChanged: (updatedSet) {
                                  setState(() {
                                    exercise.sets[setIdx] = updatedSet;
                                  });
                                },
                              ),
                            );
                          }),
                          const SizedBox(height: 8),
                          Align(
                            alignment: Alignment.centerLeft,
                            child: TextButton.icon(
                              onPressed: () {
                                setState(() {
                                  final updatedSets = List<SetLog>.from(exercise.sets)
                                    ..add(SetLog(
                                      setNumber: exercise.sets.length + 1,
                                      weight: 0.0,
                                      reps: 0,
                                      rir: 2,
                                      isCompleted: false,
                                    ));
                                  _exerciseLogs[index] = ExerciseLog(
                                    exerciseId: exercise.exerciseId,
                                    exerciseName: exercise.exerciseName,
                                    sets: updatedSets,
                                  );
                                });
                              },
                              icon: const Icon(Icons.add, size: 16, color: Color(0xFF6366F1)),
                              label: const Text('Add Set', style: TextStyle(color: Color(0xFF6366F1), fontWeight: FontWeight.bold)),
                            ),
                          )
                        ],
                      ),
                    ),
                  );
                }),
              ],
            ),
      bottomNavigationBar: _isLoading
          ? null
          : SafeArea(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF6366F1),
                    foregroundColor: Colors.white,
                    minimumSize: const Size.fromHeight(50),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  onPressed: _finishSession,
                  child: const Text(
                    'Finish Session',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                  ),
                ),
              ),
            ),
    );
  }
}

class WorkoutSetRow extends StatefulWidget {
  final SetLog setLog;
  final ValueChanged<SetLog> onChanged;

  const WorkoutSetRow({
    super.key,
    required this.setLog,
    required this.onChanged,
  });

  @override
  State<WorkoutSetRow> createState() => _WorkoutSetRowState();
}

class _WorkoutSetRowState extends State<WorkoutSetRow> {
  late TextEditingController _weightController;
  late TextEditingController _repsController;

  @override
  void initState() {
    super.initState();
    _weightController = TextEditingController(
      text: widget.setLog.weight > 0 ? widget.setLog.weight.toString() : '',
    );
    _repsController = TextEditingController(
      text: widget.setLog.reps > 0 ? widget.setLog.reps.toString() : '',
    );
  }

  @override
  void dispose() {
    _weightController.dispose();
    _repsController.dispose();
    super.dispose();
  }

  void _triggerChange() {
    final weight = double.tryParse(_weightController.text) ?? 0.0;
    final reps = int.tryParse(_repsController.text) ?? 0;
    widget.onChanged(SetLog(
      setNumber: widget.setLog.setNumber,
      weight: weight,
      reps: reps,
      rir: widget.setLog.rir,
      isCompleted: widget.setLog.isCompleted,
    ));
  }

  @override
  Widget build(BuildContext context) {
    final weight = double.tryParse(_weightController.text) ?? 0.0;
    final reps = int.tryParse(_repsController.text) ?? 0;
    final est1RM = (weight > 0 && reps > 0) ? (weight * (1 + reps / 30.0)).toStringAsFixed(1) : null;

    return Container(
      padding: const EdgeInsets.symmetric(vertical: 4, horizontal: 8),
      decoration: BoxDecoration(
        color: widget.setLog.isCompleted 
            ? const Color(0xFF10B981).withValues(alpha: 0.05) 
            : Colors.transparent,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Text('#${widget.setLog.setNumber}', style: const TextStyle(color: Colors.grey, fontSize: 13)),
          const SizedBox(width: 12),
          Expanded(
            child: SizedBox(
              height: 38,
              child: TextField(
                controller: _weightController,
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                style: const TextStyle(color: Colors.white),
                decoration: const InputDecoration(
                  hintText: 'kg',
                  hintStyle: TextStyle(color: Colors.grey),
                  contentPadding: EdgeInsets.symmetric(horizontal: 8),
                  border: OutlineInputBorder(),
                ),
                onChanged: (_) => _triggerChange(),
              ),
            ),
          ),
          const SizedBox(width: 8),
          const Text('x', style: TextStyle(color: Colors.grey)),
          const SizedBox(width: 8),
          Expanded(
            child: SizedBox(
              height: 38,
              child: TextField(
                controller: _repsController,
                keyboardType: TextInputType.number,
                style: const TextStyle(color: Colors.white),
                decoration: const InputDecoration(
                  hintText: 'reps',
                  hintStyle: TextStyle(color: Colors.grey),
                  contentPadding: EdgeInsets.symmetric(horizontal: 8),
                  border: OutlineInputBorder(),
                ),
                onChanged: (_) => _triggerChange(),
              ),
            ),
          ),
          const SizedBox(width: 12),
          DropdownButton<int>(
            value: widget.setLog.rir,
            dropdownColor: const Color(0xFF121324),
            style: const TextStyle(color: Colors.white),
            underline: const SizedBox(),
            items: List.generate(6, (index) => DropdownMenuItem(
              value: index,
              child: Text('RIR $index', style: const TextStyle(fontSize: 13)),
            )),
            onChanged: (val) {
              if (val != null) {
                widget.onChanged(SetLog(
                  setNumber: widget.setLog.setNumber,
                  weight: widget.setLog.weight,
                  reps: widget.setLog.reps,
                  rir: val,
                  isCompleted: widget.setLog.isCompleted,
                ));
              }
            },
          ),
          const SizedBox(width: 8),
          if (est1RM != null)
            Padding(
              padding: const EdgeInsets.only(right: 8.0),
              child: Text(
                '1RM: $est1RM kg',
                style: const TextStyle(color: Color(0xFF6366F1), fontSize: 11, fontWeight: FontWeight.bold),
              ),
            ),
          IconButton(
            icon: Icon(
              widget.setLog.isCompleted ? Icons.check_circle : Icons.radio_button_unchecked,
              color: widget.setLog.isCompleted ? const Color(0xFF10B981) : Colors.grey,
            ),
            onPressed: () {
              widget.onChanged(SetLog(
                setNumber: widget.setLog.setNumber,
                weight: widget.setLog.weight,
                reps: widget.setLog.reps,
                rir: widget.setLog.rir,
                isCompleted: !widget.setLog.isCompleted,
              ));
            },
          ),
        ],
      ),
    );
  }
}

class SkeletonLoader extends StatefulWidget {
  final double width;
  final double height;
  final BorderRadius borderRadius;

  const SkeletonLoader({
    super.key,
    required this.width,
    required this.height,
    this.borderRadius = const BorderRadius.all(Radius.circular(8)),
  });

  @override
  State<SkeletonLoader> createState() => _SkeletonLoaderState();
}

class _SkeletonLoaderState extends State<SkeletonLoader> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    )..repeat();
    _animation = Tween<double>(begin: -2.0, end: 2.0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOutSine),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        return Container(
          width: widget.width,
          height: widget.height,
          decoration: BoxDecoration(
            borderRadius: widget.borderRadius,
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: const [
                Color(0xFF16172B),
                Color(0xFF282944),
                Color(0xFF16172B),
              ],
              stops: [
                (0.5 + _animation.value * 0.25).clamp(0.0, 1.0),
                (0.6 + _animation.value * 0.25).clamp(0.0, 1.0),
                (0.7 + _animation.value * 0.25).clamp(0.0, 1.0),
              ],
            ),
            border: Border.all(color: const Color(0xFF1F2035), width: 1),
          ),
        );
      },
    );
  }
}
