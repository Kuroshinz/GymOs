import 'package:flutter/material.dart';
import '../../../core/network/api_client.dart';
import '../domain/gymos_state_model.dart';

class DashboardPage extends StatefulWidget {
  const DashboardPage({super.key});

  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  final ApiClient _apiClient = ApiClient();
  GymAppState? _appState;
  bool _isLoading = true;
  int _completedWorkoutsCount = 12;
  double _activeTimeMinutes = 45.0;
  double _recoveryScore = 94.0;
  final double _avgRir = 1.8;

  @override
  void initState() {
    super.initState();
    _loadDashboardData();
  }

  Future<void> _loadDashboardData() async {
    setState(() {
      _isLoading = true;
    });
    try {
      final responses = await Future.wait([
        _apiClient.fetchUnifiedDashboardState(),
        _apiClient.fetchWorkoutSessions(),
      ]);

      final GymAppState stateData = responses[0] as GymAppState;
      final sessionsData = responses[1] as Map<String, dynamic>;

      final sessions = sessionsData['sessions'] as List<dynamic>? ?? [];
      final int count = sessionsData['total_count'] as int? ?? sessions.length;

      double totalDuration = 0.0;
      for (var s in sessions) {
        totalDuration += (s['duration_minutes'] as num?)?.toDouble() ?? 0.0;
      }

      setState(() {
        _appState = stateData;
        _recoveryScore = stateData.recoveryScore.toDouble();
        _completedWorkoutsCount = count;
        if (totalDuration > 0) {
          _activeTimeMinutes = totalDuration;
        }
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
    }
  }

  void _showLogMealModal() {
    final nameController = TextEditingController();
    final caloriesController = TextEditingController();
    final proteinController = TextEditingController();
    final carbsController = TextEditingController();
    final fatController = TextEditingController();

    showDialog(
      context: context,
      builder: (dialogContext) {
        return AlertDialog(
          backgroundColor: const Color(0xFF121324),
          title: const Text('Log Meal', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: nameController,
                  style: const TextStyle(color: Colors.white),
                  decoration: const InputDecoration(labelText: 'Meal Name', labelStyle: TextStyle(color: Colors.grey)),
                ),
                TextField(
                  controller: caloriesController,
                  keyboardType: TextInputType.number,
                  style: const TextStyle(color: Colors.white),
                  decoration: const InputDecoration(labelText: 'Calories (kcal)', labelStyle: TextStyle(color: Colors.grey)),
                ),
                TextField(
                  controller: proteinController,
                  keyboardType: TextInputType.number,
                  style: const TextStyle(color: Colors.white),
                  decoration: const InputDecoration(labelText: 'Protein (g)', labelStyle: TextStyle(color: Colors.grey)),
                ),
                TextField(
                  controller: carbsController,
                  keyboardType: TextInputType.number,
                  style: const TextStyle(color: Colors.white),
                  decoration: const InputDecoration(labelText: 'Carbs (g)', labelStyle: TextStyle(color: Colors.grey)),
                ),
                TextField(
                  controller: fatController,
                  keyboardType: TextInputType.number,
                  style: const TextStyle(color: Colors.white),
                  decoration: const InputDecoration(labelText: 'Fat (g)', labelStyle: TextStyle(color: Colors.grey)),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(dialogContext).pop(),
              child: const Text('Cancel', style: TextStyle(color: Colors.grey)),
            ),
            ElevatedButton(
              style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF6366F1)),
              onPressed: () async {
                final name = nameController.text.trim();
                final calories = double.tryParse(caloriesController.text) ?? 0.0;
                final protein = double.tryParse(proteinController.text) ?? 0.0;
                final carbs = double.tryParse(carbsController.text) ?? 0.0;
                final fat = double.tryParse(fatController.text) ?? 0.0;

                if (name.isNotEmpty && calories > 0) {
                  final messenger = ScaffoldMessenger.of(context);
                  Navigator.of(dialogContext).pop();
                  setState(() {
                    _isLoading = true;
                  });
                  try {
                    final success = await _apiClient.postNutritionLog(
                      name: name,
                      calories: calories,
                      proteinG: protein,
                      carbsG: carbs,
                      fatG: fat,
                    );
                    if (success) {
                      _loadDashboardData();
                    }
                  } catch (e) {
                    setState(() {
                      _isLoading = false;
                    });
                    messenger.showSnackBar(
                      SnackBar(content: Text('Failed to log meal: $e'), backgroundColor: const Color(0xFFEF4444)),
                    );
                  }
                }
              },
              child: const Text('Log', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
            ),
          ],
        );
      },
    );
  }

  Widget _buildNutritionSection() {
    final summary = _appState?.nutritionSummary;
    if (summary == null) {
      return Card(
        color: const Color(0xFF121324),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        child: const Padding(
          padding: EdgeInsets.all(20.0),
          child: Center(
            child: Text('Log meal to see stats.', style: TextStyle(color: Colors.grey)),
          ),
        ),
      );
    }

    return Card(
      color: const Color(0xFF121324),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Nutrition Tracker',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white),
                ),
                ElevatedButton.icon(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF6366F1),
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                  onPressed: _showLogMealModal,
                  icon: const Icon(Icons.add, size: 16),
                  label: const Text('Log Meal'),
                ),
              ],
            ),
            const SizedBox(height: 20),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text('Calories', style: TextStyle(color: Colors.grey)),
                    Text(summary.caloriesDisplay, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                  ],
                ),
                const SizedBox(height: 8),
                ClipRRect(
                  borderRadius: BorderRadius.circular(4),
                  child: LinearProgressIndicator(
                    value: (summary.caloriesPct / 100.0).clamp(0.0, 1.0),
                    minHeight: 8,
                    backgroundColor: const Color(0xFF1F2035),
                    valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFF6366F1)),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),
            Row(
              children: [
                Expanded(child: _buildMacroColumn('Protein', summary.proteinDisplay, summary.proteinPct / 100.0, Colors.teal)),
                const SizedBox(width: 16),
                Expanded(child: _buildMacroColumn('Carbs', summary.carbsDisplay, summary.carbsPct / 100.0, Colors.orange)),
                const SizedBox(width: 16),
                Expanded(child: _buildMacroColumn('Fat', summary.fatDisplay, summary.fatPct / 100.0, const Color(0xFFEF4444))),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMacroColumn(String name, String display, double value, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(name, style: const TextStyle(color: Colors.grey, fontSize: 13)),
        const SizedBox(height: 4),
        Text(display, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12)),
        const SizedBox(height: 8),
        ClipRRect(
          borderRadius: BorderRadius.circular(2),
          child: LinearProgressIndicator(
            value: value.clamp(0.0, 1.0),
            minHeight: 4,
            backgroundColor: const Color(0xFF1F2035),
            valueColor: AlwaysStoppedAnimation<Color>(color),
          ),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final titleText = _appState?.activeProgramName ?? 'PPL-UL Master v6';

    return Scaffold(
      backgroundColor: const Color(0xFF070814),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Dashboard',
                        style: TextStyle(
                          fontSize: 28,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Welcome back, Nguyễn Thiện Nhân. Active program: $titleText',
                        style: const TextStyle(
                          fontSize: 14,
                          color: Colors.grey,
                        ),
                      ),
                    ],
                  ),
                  IconButton(
                    icon: const Icon(Icons.refresh, color: Color(0xFF6366F1)),
                    onPressed: _loadDashboardData,
                  ),
                ],
              ),
              const SizedBox(height: 24),
              _isLoading
                  ? const Expanded(
                      child: Center(
                        child: CircularProgressIndicator(color: Color(0xFF6366F1)),
                      ),
                    )
                  : Expanded(
                      child: ListView(
                        children: [
                          GridView.count(
                            shrinkWrap: true,
                            physics: const NeverScrollableScrollPhysics(),
                            crossAxisCount: 2,
                            crossAxisSpacing: 16,
                            mainAxisSpacing: 16,
                            childAspectRatio: 1.5,
                            children: [
                              _buildStatCard(
                                title: 'Active Time',
                                value: '${_activeTimeMinutes.toInt()} mins',
                                subtitle: 'Total volume logged',
                                icon: Icons.timer_outlined,
                                color: const Color(0xFF6366F1),
                              ),
                              _buildStatCard(
                                title: 'Workouts',
                                value: '$_completedWorkoutsCount completed',
                                subtitle: 'Across PPL programs',
                                icon: Icons.fitness_center_outlined,
                                color: const Color(0xFF8B5CF6),
                              ),
                              _buildStatCard(
                                title: 'Recovery Score',
                                value: '${_recoveryScore.toInt()}%',
                                subtitle: _recoveryScore >= 80 ? 'Excellent' : 'Moderate Fatigue',
                                icon: Icons.battery_charging_full_outlined,
                                color: _appState?.recoveryColor ?? Colors.teal,
                              ),
                              _buildStatCard(
                                title: 'Avg RIR',
                                value: '$_avgRir reps',
                                subtitle: 'High effort training',
                                icon: Icons.speed_outlined,
                                color: Colors.orange,
                              ),
                            ],
                          ),
                          const SizedBox(height: 24),
                          _buildNutritionSection(),
                        ],
                      ),
                    ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatCard({
    required String title,
    required String value,
    required String subtitle,
    required IconData icon,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFF121324),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF1F2035)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                title,
                style: const TextStyle(
                  color: Colors.grey,
                  fontSize: 14,
                ),
              ),
              Icon(icon, color: color, size: 24),
            ],
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                value,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                subtitle,
                style: const TextStyle(
                  color: Colors.grey,
                  fontSize: 12,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
