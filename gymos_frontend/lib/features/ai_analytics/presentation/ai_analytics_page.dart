import 'package:flutter/material.dart';
import '../../../core/network/api_client.dart';
import '../../dashboard/domain/gymos_state_model.dart';
import '../domain/ai_prediction_models.dart';

class AIAnalyticsPage extends StatefulWidget {
  const AIAnalyticsPage({super.key});

  @override
  State<AIAnalyticsPage> createState() => _AIAnalyticsPageState();
}

class _AIAnalyticsPageState extends State<AIAnalyticsPage> {
  final ApiClient _apiClient = ApiClient();
  
  // State variables for simulator
  double _sleepHours = 8.0;
  double _stressLevel = 2.0; // 1 to 5
  double _sorenessLevel = 2.0; // 1 to 5
  
  // Loaded data from APIs
  bool _isLoading = true;
  String? _error;
  
  int _recoveryScore = 85;
  String _readinessLevel = 'Optimal';
  String _readinessDesc = 'Loading recovery details...';
  
  String _hypertrophyInsights = 'Fetching hypertrophy recommendations from GymOS AI...';
  String _readinessSummary = '';
  List<dynamic> _muscleFatigue = [];
  GymAppState? _appState;

  @override
  void initState() {
    super.initState();
    _fetchData();
  }

  Future<void> _fetchData() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      final state = await _apiClient.fetchUnifiedDashboardState();
      final aiResponse = await _apiClient.getAiData();

      setState(() {
        _appState = state;
        _recoveryScore = state.recoveryScore;
        
        // Dynamic color hex evaluation for recovery score
        if (state.recoveryScore >= 85) {
          _readinessLevel = 'Optimal';
          _readinessDesc = 'Muscles are sufficiently repaired. Ready to progress!';
        } else if (state.recoveryScore >= 70) {
          _readinessLevel = 'Good';
          _readinessDesc = 'Good recovery level. Suitable for loading.';
        } else if (state.recoveryScore >= 55) {
          _readinessLevel = 'Moderate';
          _readinessDesc = 'Accumulated fatigue detected. dropping sets recommended.';
        } else {
          _readinessLevel = 'Critical';
          _readinessDesc = 'High recovery deficit. We recommend rest.';
        }
        
        // Map dynamic muscleStatus entries to list fatigue
        _muscleFatigue = state.muscleStatus.entries.map((entry) => {
          'name': entry.key,
          'fatigue_pct': entry.value.fatigue,
        }).toList();
        
        _hypertrophyInsights = aiResponse['hypertrophy_insights'] ?? 'No insights generated.';
        _readinessSummary = aiResponse['readiness_summary'] ?? '';
        
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _updatePredictions() async {
    setState(() {
      _isLoading = true;
    });
    try {
      final request = AiPredictionRequest(
        sleepHours: _sleepHours,
        stressLevel: _stressLevel.toInt(),
        sorenessLevel: _sorenessLevel.toInt(),
      );
      final response = await _apiClient.getAiPrediction(request);
      setState(() {
        _recoveryScore = response.readinessScore.toInt();
        _readinessDesc = response.insightText;
        if (_recoveryScore >= 85) {
          _readinessLevel = 'Optimal';
        } else if (_recoveryScore >= 70) {
          _readinessLevel = 'Good';
        } else if (_recoveryScore >= 55) {
          _readinessLevel = 'Moderate';
        } else {
          _readinessLevel = 'Critical';
        }
      });
    } catch (e) {
      // getAiPrediction returns fallback values on network error
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  // Counterfactual calculation
  double get _simulatedPerformance {
    // Standard baseline is 75
    double sleepFactor = (_sleepHours - 8.0) * 5.0;
    double stressFactor = (_stressLevel - 2) * -6.0;
    double sorenessFactor = (_sorenessLevel - 2) * -8.0;
    
    double score = 75.0 + sleepFactor + stressFactor + sorenessFactor;
    return score.clamp(0.0, 100.0);
  }

  String get _simulatorFeedback {
    final score = _simulatedPerformance;
    if (score >= 85) return 'Optimal Readiness. Ready to push high intensity and progressive overload.';
    if (score >= 70) return 'Good readiness. Normal training volume is recommended.';
    if (score >= 55) return 'CNS fatigue detected. Consider avoiding training to failure or reduce intensity.';
    return 'Severe recovery deficit. High risk of injury. Recommend active recovery or rest.';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF070814),
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: _fetchData,
          color: const Color(0xFF6366F1),
          backgroundColor: const Color(0xFF121324),
          child: SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.all(24.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'AI Analytics & Predictions',
                          style: TextStyle(
                            fontSize: 28,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                            letterSpacing: 0.5,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Simulate counterfactual scenarios and access deep hypertrophy insights.',
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.grey[400],
                          ),
                        ),
                      ],
                    ),
                    if (_isLoading)
                      const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Color(0xFF6366F1),
                        ),
                      )
                    else
                      IconButton(
                        onPressed: _fetchData,
                        icon: const Icon(Icons.refresh, color: Colors.grey),
                        tooltip: 'Sync data',
                      ),
                  ],
                ),
                
                if (_error != null) ...[
                  const SizedBox(height: 16),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                    decoration: BoxDecoration(
                      color: Colors.redAccent.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.redAccent.withValues(alpha: 0.3)),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.error_outline, color: Colors.redAccent, size: 20),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            'Warning: Offline mode active. Using local prediction baseline ($errorText).',
                            style: const TextStyle(color: Colors.redAccent, fontSize: 13),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
                
                const SizedBox(height: 24),

                // Main Layout Grid-like Layout
                LayoutBuilder(
                  builder: (context, constraints) {
                    final isWide = constraints.maxWidth > 900;
                    return Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        if (isWide)
                          Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Expanded(flex: 3, child: _buildRecoveryCard()),
                              const SizedBox(width: 24),
                              Expanded(flex: 4, child: _buildInsightsCard()),
                            ],
                          )
                        else ...[
                          _buildRecoveryCard(),
                          const SizedBox(height: 24),
                          _buildInsightsCard(),
                        ],
                        const SizedBox(height: 24),
                        _buildNutritionDonutsCard(),
                        const SizedBox(height: 24),
                        _buildSimulatorPanel(),
                        const SizedBox(height: 24),
                        _buildMuscleFatiguePanel(),
                      ],
                    );
                  },
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  String get errorText => _error != null && _error!.contains('Exception: ') 
      ? _error!.replaceAll('Exception: ', '') 
      : 'Connection error';

  Color _getScoreColor(double score) {
    if (score >= 85) return const Color(0xFF34D399); // Success (Teal)
    if (score >= 70) return const Color(0xFF38BDF8); // Info/Secondary (Blue)
    if (score >= 55) return const Color(0xFFFBBF24); // Warning (Yellow)
    return const Color(0xFFFB7185); // Error (Red)
  }

  Widget _buildRecoveryCard() {
    final ringColor = _getScoreColor(_recoveryScore.toDouble());

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: const Color(0xFF121324),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF1F2035)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.healing_outlined, color: Color(0xFF34D399), size: 20),
              SizedBox(width: 8),
              Text(
                'Recovery Predictor',
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          Center(
            child: Stack(
              alignment: Alignment.center,
              children: [
                SizedBox(
                  width: 140,
                  height: 140,
                  child: CircularProgressIndicator(
                    value: _recoveryScore / 100.0,
                    strokeWidth: 10,
                    backgroundColor: const Color(0xFF1A1B2F),
                    valueColor: AlwaysStoppedAnimation<Color>(ringColor),
                  ),
                ),
                Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      '$_recoveryScore%',
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 32,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      _readinessLevel.toUpperCase(),
                      style: TextStyle(
                        color: Colors.grey[400],
                        fontSize: 11,
                        letterSpacing: 1.5,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),
          if (_isLoading) ...[
            const SkeletonLoader(width: double.infinity, height: 16),
            const SizedBox(height: 8),
            const SkeletonLoader(width: 150, height: 16),
          ] else ...[
            Text(
              _readinessDesc,
              textAlign: TextAlign.center,
              style: TextStyle(
                color: Colors.grey[300],
                fontSize: 14,
                height: 1.4,
              ),
            ),
            if (_readinessSummary.isNotEmpty) ...[
              const SizedBox(height: 12),
              Text(
                _readinessSummary,
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: Colors.grey[400],
                  fontSize: 12,
                  fontStyle: FontStyle.italic,
                ),
              ),
            ],
          ],
        ],
      ),
    );
  }

  Widget _buildInsightsCard() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF121324), Color(0xFF16152F)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF1F2035)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Row(
                children: [
                  Icon(Icons.psychology_outlined, color: Color(0xFF8B5CF6), size: 22),
                  SizedBox(width: 8),
                  Text(
                    'Hypertrophy Insights',
                    style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: const Color(0xFF8B5CF6).withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFF8B5CF6).withValues(alpha: 0.3)),
                ),
                child: const Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.bolt, color: Color(0xFF8B5CF6), size: 12),
                    SizedBox(width: 4),
                    Text(
                      'AI ACTIVE',
                      style: TextStyle(
                        color: Color(0xFF8B5CF6),
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          if (_isLoading) ...[
            const SkeletonLoader(width: double.infinity, height: 16),
            const SizedBox(height: 8),
            const SkeletonLoader(width: double.infinity, height: 16),
            const SizedBox(height: 8),
            const SkeletonLoader(width: 200, height: 16),
          ] else ...[
            Text(
              _hypertrophyInsights,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 14.5,
                height: 1.6,
              ),
            ),
          ],
          const SizedBox(height: 24),
          Row(
            children: [
              Expanded(
                child: Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: const Color(0xFF0F1020),
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: const Color(0xFF1F2035)),
                  ),
                  child: const Row(
                    children: [
                      Icon(Icons.fitness_center_outlined, color: Colors.blueAccent, size: 18),
                      SizedBox(width: 10),
                      Expanded(
                        child: Text(
                          'Ideal Reps: 8-12 / set',
                          style: TextStyle(color: Colors.white, fontSize: 12),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: const Color(0xFF0F1020),
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: const Color(0xFF1F2035)),
                  ),
                  child: const Row(
                    children: [
                      Icon(Icons.query_stats_outlined, color: Colors.orange, size: 18),
                      SizedBox(width: 10),
                      Expanded(
                        child: Text(
                          'Optimal Volume: 18 Sets',
                          style: TextStyle(color: Colors.white, fontSize: 12),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSimulatorPanel() {
    final simulatedScore = _simulatedPerformance;

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: const Color(0xFF121324),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF1F2035)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.insights, color: Color(0xFF6366F1), size: 20),
              SizedBox(width: 8),
              Text(
                'Counterfactual Simulator Panel',
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            'Dynamically tweak parameters to simulate recovery effects on predicted readiness output.',
            style: TextStyle(
              color: Colors.grey[400],
              fontSize: 13,
            ),
          ),
          const SizedBox(height: 24),
          
          LayoutBuilder(
            builder: (context, constraints) {
              final isWide = constraints.maxWidth > 700;
              
              final content = [
                // Sleep hours
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text('Sleep Hours', style: TextStyle(color: Colors.white, fontSize: 14)),
                        Text('${_sleepHours.toStringAsFixed(1)} hrs', style: const TextStyle(color: Color(0xFF6366F1), fontWeight: FontWeight.bold)),
                      ],
                    ),
                    Slider(
                      value: _sleepHours,
                      min: 4.0,
                      max: 12.0,
                      activeColor: const Color(0xFF6366F1),
                      inactiveColor: const Color(0xFF1F2035),
                      onChanged: (val) {
                        setState(() {
                          _sleepHours = val;
                        });
                      },
                      onChangeEnd: (val) {
                        _updatePredictions();
                      },
                    ),
                  ],
                ),
                
                // Stress level
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text('Stress Level (1: Low, 5: High)', style: TextStyle(color: Colors.white, fontSize: 14)),
                        Text('${_stressLevel.toInt()} / 5', style: const TextStyle(color: Color(0xFF6366F1), fontWeight: FontWeight.bold)),
                      ],
                    ),
                    Slider(
                      value: _stressLevel,
                      min: 1.0,
                      max: 5.0,
                      divisions: 4,
                      activeColor: const Color(0xFF6366F1),
                      inactiveColor: const Color(0xFF1F2035),
                      onChanged: (val) {
                        setState(() {
                          _stressLevel = val;
                        });
                      },
                      onChangeEnd: (val) {
                        _updatePredictions();
                      },
                    ),
                  ],
                ),
                
                // Soreness level
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text('Muscle Soreness (1: None, 5: Severe)', style: TextStyle(color: Colors.white, fontSize: 14)),
                        Text('${_sorenessLevel.toInt()} / 5', style: const TextStyle(color: Color(0xFF6366F1), fontWeight: FontWeight.bold)),
                      ],
                    ),
                    Slider(
                      value: _sorenessLevel,
                      min: 1.0,
                      max: 5.0,
                      divisions: 4,
                      activeColor: const Color(0xFF6366F1),
                      inactiveColor: const Color(0xFF1F2035),
                      onChanged: (val) {
                        setState(() {
                          _sorenessLevel = val;
                        });
                      },
                      onChangeEnd: (val) {
                        _updatePredictions();
                      },
                    ),
                  ],
                ),
              ];
              
              if (isWide) {
                return Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      flex: 4,
                      child: Column(
                        children: [
                          content[0],
                          const SizedBox(height: 16),
                          content[1],
                          const SizedBox(height: 16),
                          content[2],
                        ],
                      ),
                    ),
                    const SizedBox(width: 32),
                    Expanded(
                      flex: 3,
                      child: _buildSimulatorResultCard(simulatedScore),
                    ),
                  ],
                );
              } else {
                return Column(
                  children: [
                    content[0],
                    const SizedBox(height: 16),
                    content[1],
                    const SizedBox(height: 16),
                    content[2],
                    const SizedBox(height: 24),
                    _buildSimulatorResultCard(simulatedScore),
                  ],
                );
              }
            },
          ),
        ],
      ),
    );
  }

  Widget _buildSimulatorResultCard(double score) {
    Color scoreColor = _getScoreColor(score);

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFF0F1020),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFF1F2035)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Text(
            'Simulated Readiness Score',
            style: TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          Text(
            '${score.toStringAsFixed(0)}%',
            style: TextStyle(
              color: scoreColor,
              fontSize: 48,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          Text(
            _simulatorFeedback,
            textAlign: TextAlign.center,
            style: TextStyle(
              color: Colors.grey[300],
              fontSize: 13,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 16),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: score / 100.0,
              backgroundColor: const Color(0xFF1A1B2F),
              valueColor: AlwaysStoppedAnimation<Color>(scoreColor),
              minHeight: 6,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMuscleFatiguePanel() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: const Color(0xFF121324),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF1F2035)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.bar_chart, color: Color(0xFF10B981), size: 20),
              SizedBox(width: 8),
              Text(
                'Muscle Fatigue (Inroad) Status',
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            'Estimated inroad/fatigue based on logged sets vs. weekly recovery thresholds.',
            style: TextStyle(color: Colors.grey[400], fontSize: 13),
          ),
          const SizedBox(height: 24),
          if (_muscleFatigue.isEmpty)
            const Text('No fatigue data logged yet.', style: TextStyle(color: Colors.grey))
          else
            ..._muscleFatigue.map((item) {
              final String name = item['name'] ?? '';
              final double val = (item['fatigue_pct'] as num?)?.toDouble() ?? 0.0;
              return Padding(
                padding: const EdgeInsets.only(bottom: 16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(name, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                        Text('${val.toInt()}%', style: TextStyle(color: _getScoreColor(100 - val), fontWeight: FontWeight.bold)),
                      ],
                    ),
                    const SizedBox(height: 8),
                    ClipRRect(
                      borderRadius: BorderRadius.circular(2),
                      child: LinearProgressIndicator(
                        value: val / 100.0,
                        minHeight: 6,
                        backgroundColor: const Color(0xFF1F2035),
                        valueColor: AlwaysStoppedAnimation<Color>(_getScoreColor(100 - val)),
                      ),
                    ),
                  ],
                ),
              );
            }),
        ],
      ),
    );
  }

  Widget _buildNutritionDonutsCard() {
    final summary = _appState?.nutritionSummary;
    if (summary == null) return const SizedBox();

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: const Color(0xFF121324),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF1F2035)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.restaurant_menu, color: Color(0xFF8B5CF6), size: 20),
              SizedBox(width: 8),
              Text(
                'Nutrition Macro Progress',
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildMacroDonut('Protein', summary.proteinDisplay, summary.proteinPct / 100.0, Colors.teal),
              _buildMacroDonut('Carbs', summary.carbsDisplay, summary.carbsPct / 100.0, Colors.orange),
              _buildMacroDonut('Fat', summary.fatDisplay, summary.fatPct / 100.0, const Color(0xFFEF4444)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildMacroDonut(String label, String display, double value, Color color) {
    return Column(
      children: [
        Stack(
          alignment: Alignment.center,
          children: [
            SizedBox(
              width: 70,
              height: 70,
              child: CircularProgressIndicator(
                value: value.clamp(0.0, 1.0),
                strokeWidth: 6,
                backgroundColor: const Color(0xFF1A1B2F),
                valueColor: AlwaysStoppedAnimation<Color>(color),
              ),
            ),
            Text(
              '${(value * 100).toInt()}%',
              style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 13, fontWeight: FontWeight.bold)),
        const SizedBox(height: 4),
        Text(display.split(' / ').first, style: TextStyle(color: color, fontSize: 12, fontWeight: FontWeight.bold)),
      ],
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
