import 'package:flutter/material.dart';
import '../../../core/network/api_client.dart';

class AIAnalyticsPage extends StatefulWidget {
  const AIAnalyticsPage({super.key});

  @override
  State<AIAnalyticsPage> createState() => _AIAnalyticsPageState();
}

class _AIAnalyticsPageState extends State<AIAnalyticsPage> {
  final ApiClient _apiClient = ApiClient();
  
  // State variables for simulator
  double _sleepHours = 8.0;
  double _nutritionScore = 3.0; // 1 to 5
  double _weeklySets = 15.0; // 5 to 30
  
  // Loaded data from APIs
  bool _isLoading = true;
  String? _error;
  
  int _recoveryScore = 85;
  String _readinessLevel = 'Optimal';
  String _readinessDesc = 'Loading recovery details...';
  
  String _hypertrophyInsights = 'Fetching hypertrophy recommendations from GymOS AI...';
  String _readinessSummary = '';

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
      final recoveryResponse = await _apiClient.getRecoveryData();
      final aiResponse = await _apiClient.getAiData();

      setState(() {
        // Handle Recovery Data
        if (recoveryResponse['readiness'] != null) {
          final readiness = recoveryResponse['readiness'];
          _recoveryScore = readiness['score']?.toInt() ?? 85;
          _readinessLevel = readiness['level'] ?? 'Optimal';
          _readinessDesc = readiness['description'] ?? 'Muscles are sufficiently repaired.';
        } else if (recoveryResponse['today_score'] != null) {
          _recoveryScore = recoveryResponse['today_score']?.toInt() ?? 85;
        }
        
        // Handle AI insights
        _hypertrophyInsights = aiResponse['hypertrophy_insights'] ?? 'No insights generated.';
        _readinessSummary = aiResponse['readiness_summary'] ?? '';
        
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
        // Keep placeholders if they fail but show error indicator at top
      });
    }
  }

  // Counterfactual calculation
  double get _simulatedPerformance {
    double sleepWeight = _sleepHours / 8.0; // Optimal: 8
    if (sleepWeight > 1.2) sleepWeight = 1.2;
    
    double nutritionWeight = _nutritionScore / 4.0; // Optimal: 4
    if (nutritionWeight > 1.2) nutritionWeight = 1.2;
    
    // Volume optimal around 16-20 sets, penalty for under or over-training
    double volumeFactor = 1.0 - ((_weeklySets - 18.0).abs() / 25.0);
    if (volumeFactor < 0) volumeFactor = 0.0;
    
    double score = (sleepWeight * 0.4 + nutritionWeight * 0.3 + volumeFactor * 0.3) * 100.0;
    return score.clamp(0.0, 100.0);
  }

  String get _simulatorFeedback {
    final score = _simulatedPerformance;
    if (score >= 90) return 'Peak Performance (Optimal Recovery)';
    if (score >= 75) return 'Good readiness. Ready for progressive overload.';
    if (score >= 60) return 'Moderate strain. Recommend matching set volume to MRV.';
    return 'High risk of overreaching. Prioritize sleep & rest.';
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
                      color: Colors.redAccent.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.redAccent.withOpacity(0.3)),
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
                        _buildSimulatorPanel(),
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

  Widget _buildRecoveryCard() {
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
              Icon(Icons.healing_outlined, color: Colors.teal, size: 20),
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
                    valueColor: const AlwaysStoppedAnimation<Color>(Colors.teal),
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
                  color: const Color(0xFF8B5CF6).withOpacity(0.15),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFF8B5CF6).withOpacity(0.3)),
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
          Text(
            _hypertrophyInsights,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 14.5,
              height: 1.6,
            ),
          ),
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
            'Dynamically tweak parameters to simulate recovery effects on predicted output.',
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
                    ),
                  ],
                ),
                
                // Nutrition rating
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text('Nutrition Quality', style: TextStyle(color: Colors.white, fontSize: 14)),
                        Text('${_nutritionScore.toInt()} / 5', style: const TextStyle(color: Color(0xFF6366F1), fontWeight: FontWeight.bold)),
                      ],
                    ),
                    Slider(
                      value: _nutritionScore,
                      min: 1.0,
                      max: 5.0,
                      divisions: 4,
                      activeColor: const Color(0xFF6366F1),
                      inactiveColor: const Color(0xFF1F2035),
                      onChanged: (val) {
                        setState(() {
                          _nutritionScore = val;
                        });
                      },
                    ),
                  ],
                ),
                
                // Weekly Sets (Volume)
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text('Weekly Target Sets (Volume)', style: TextStyle(color: Colors.white, fontSize: 14)),
                        Text('${_weeklySets.toInt()} sets', style: const TextStyle(color: Color(0xFF6366F1), fontWeight: FontWeight.bold)),
                      ],
                    ),
                    Slider(
                      value: _weeklySets,
                      min: 5.0,
                      max: 30.0,
                      activeColor: const Color(0xFF6366F1),
                      inactiveColor: const Color(0xFF1F2035),
                      onChanged: (val) {
                        setState(() {
                          _weeklySets = val;
                        });
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
    Color scoreColor;
    if (score >= 90) {
      scoreColor = Colors.tealAccent;
    } else if (score >= 70) {
      scoreColor = Colors.greenAccent;
    } else if (score >= 50) {
      scoreColor = Colors.orangeAccent;
    } else {
      scoreColor = Colors.redAccent;
    }

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
            'Predicted Readiness Index',
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
}
