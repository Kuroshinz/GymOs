import 'package:flutter/material.dart';
import '../../../core/network/api_client.dart';

class WorkoutPage extends StatefulWidget {
  const WorkoutPage({super.key});

  @override
  State<WorkoutPage> createState() => _WorkoutPageState();
}

class _WorkoutPageState extends State<WorkoutPage> {
  final ApiClient _apiClient = ApiClient();
  final List<ExerciseItem> _exercises = [
    ExerciseItem(name: 'Lat Pulldown', targetSets: 3),
    ExerciseItem(name: 'Chest Supported Row', targetSets: 3),
    ExerciseItem(name: 'Seated Cable Row', targetSets: 2),
    ExerciseItem(name: 'Rear Delt Fly', targetSets: 2),
  ];

  bool _isSaving = false;
  String _message = '';

  Future<void> _logSet(String name, double weight, int reps, int rir) async {
    setState(() {
      _message = 'Syncing...';
    });
    try {
      final result = await _apiClient.postWorkoutLog(
        exerciseName: name,
        weightKg: weight,
        reps: reps,
        rir: rir,
      );
      setState(() {
        _message = 'Synced: ${result['message'] ?? 'OK'}';
      });
    } catch (e) {
      setState(() {
        _message = 'Sync Failed: $e';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Workout - PULL', style: TextStyle(fontWeight: FontWeight.bold)),
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
      body: ListView.builder(
        padding: const EdgeInsets.all(16.0),
        itemCount: _exercises.length,
        itemBuilder: (context, index) {
          final exercise = _exercises[index];
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
                      Text(
                        exercise.name,
                        style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: const Color(0xFF6366F1).withOpacity(0.1),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: const Color(0xFF6366F1).withOpacity(0.3)),
                        ),
                        child: Text(
                          '${exercise.targetSets} sets',
                          style: const TextStyle(color: Color(0xFF6366F1), fontSize: 12),
                        ),
                      )
                    ],
                  ),
                  const SizedBox(height: 16),
                  ...List.generate(exercise.targetSets, (setIdx) {
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 8.0),
                      child: WorkoutSetRow(
                        setNum: setIdx + 1,
                        onChanged: (weight, reps, rir) {
                          if (weight > 0 && reps > 0) {
                            _logSet(exercise.name, weight, reps, rir);
                          }
                        },
                      ),
                    );
                  })
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}

class ExerciseItem {
  final String name;
  final int targetSets;
  ExerciseItem({required this.name, required this.targetSets});
}

class WorkoutSetRow extends StatefulWidget {
  final int setNum;
  final void Function(double weight, int reps, int rir) onChanged;

  const WorkoutSetRow({
    super.key,
    required this.setNum,
    required this.onChanged,
  });

  @override
  State<WorkoutSetRow> createState() => _WorkoutSetRowState();
}

class _WorkoutSetRowState extends State<WorkoutSetRow> {
  final TextEditingController _weightController = TextEditingController();
  final TextEditingController _repsController = TextEditingController();
  final TextEditingController _rirController = TextEditingController();

  void _triggerChange() {
    final weight = double.tryParse(_weightController.text) ?? 0.0;
    final reps = int.tryParse(_repsController.text) ?? 0;
    final rir = int.tryParse(_rirController.text) ?? 0;
    widget.onChanged(weight, reps, rir);
  }

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Text('#${widget.setNum}', style: const TextStyle(color: Colors.grey, fontSize: 13)),
        const SizedBox(width: 16),
        Expanded(
          child: SizedBox(
            height: 38,
            child: TextField(
              controller: _weightController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(
                hintText: 'kg',
                contentPadding: EdgeInsets.symmetric(horizontal: 8),
                border: OutlineInputBorder(),
              ),
              onChanged: (_) => _triggerChange(),
            ),
          ),
        ),
        const SizedBox(width: 8),
        const Text('x'),
        const SizedBox(width: 8),
        Expanded(
          child: SizedBox(
            height: 38,
            child: TextField(
              controller: _repsController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(
                hintText: 'reps',
                contentPadding: EdgeInsets.symmetric(horizontal: 8),
                border: OutlineInputBorder(),
              ),
              onChanged: (_) => _triggerChange(),
            ),
          ),
        ),
        const SizedBox(width: 16),
        const Text('RIR'),
        const SizedBox(width: 8),
        SizedBox(
          width: 48,
          height: 38,
          child: TextField(
            controller: _rirController,
            keyboardType: TextInputType.number,
            decoration: const InputDecoration(
              hintText: '-',
              contentPadding: EdgeInsets.symmetric(horizontal: 8),
              border: OutlineInputBorder(),
            ),
            onChanged: (_) => _triggerChange(),
          ),
        ),
      ],
    );
  }
}
