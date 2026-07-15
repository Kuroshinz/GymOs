import 'package:flutter/material.dart';
import '../../../core/network/api_client.dart';

class RecoveryPage extends StatefulWidget {
  const RecoveryPage({super.key});

  @override
  State<RecoveryPage> createState() => _RecoveryPageState();
}

class _RecoveryPageState extends State<RecoveryPage> {
  final ApiClient _apiClient = ApiClient();
  bool _isLoading = true;
  double _score = 88.0;
  String _level = 'Good';
  String _description = 'Muscles are sufficiently repaired. Ready to train.';
  List<dynamic> _recentScores = [];

  @override
  void initState() {
    super.initState();
    _loadRecoveryData();
  }

  Future<void> _loadRecoveryData() async {
    setState(() {
      _isLoading = true;
    });
    try {
      final data = await _apiClient.getRecoveryData();
      final readiness = data['readiness'] ?? {};
      setState(() {
        _score = (readiness['score'] as num?)?.toDouble() ?? 88.0;
        _level = readiness['level'] ?? 'Good';
        _description = readiness['description'] ?? 'Muscles are sufficiently repaired.';
        _recentScores = data['recent_scores'] ?? [];
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
        // Offline / fallback data remains
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    Color levelColor;
    if (_score >= 85) {
      levelColor = const Color(0xFF10B981);
    } else if (_score >= 70) {
      levelColor = const Color(0xFF6366F1);
    } else if (_score >= 55) {
      levelColor = Colors.orange;
    } else {
      levelColor = const Color(0xFFEF4444);
    }

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
                  const Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Recovery & Readiness',
                        style: TextStyle(
                          fontSize: 28,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      SizedBox(height: 8),
                      Text(
                        'Monitor sleep quality, stress levels, and daily muscle recovery.',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.grey,
                        ),
                      ),
                    ],
                  ),
                  IconButton(
                    icon: const Icon(Icons.refresh, color: Color(0xFF6366F1)),
                    onPressed: _loadRecoveryData,
                  ),
                ],
              ),
              const SizedBox(height: 32),
              _isLoading
                  ? const Expanded(
                      child: Center(
                        child: CircularProgressIndicator(color: Color(0xFF6366F1)),
                      ),
                    )
                  : Expanded(
                      child: ListView(
                        children: [
                          Center(
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Stack(
                                  alignment: Alignment.center,
                                  children: [
                                    SizedBox(
                                      width: 160,
                                      height: 160,
                                      child: CircularProgressIndicator(
                                        value: _score / 100.0,
                                        strokeWidth: 12,
                                        backgroundColor: const Color(0xFF16172B),
                                        color: levelColor,
                                      ),
                                    ),
                                    Column(
                                      children: [
                                        Text(
                                          '${_score.toInt()}%',
                                          style: const TextStyle(
                                            fontSize: 36,
                                            fontWeight: FontWeight.bold,
                                            color: Colors.white,
                                          ),
                                        ),
                                        const SizedBox(height: 4),
                                        Text(
                                          _level,
                                          style: TextStyle(
                                            fontSize: 16,
                                            fontWeight: FontWeight.bold,
                                            color: levelColor,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 24),
                                Text(
                                  _description,
                                  textAlign: TextAlign.center,
                                  style: const TextStyle(
                                    fontSize: 15,
                                    color: Colors.white,
                                    height: 1.4,
                                  ),
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(height: 48),
                          const Text(
                            'Recent Recovery History',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                          ),
                          const SizedBox(height: 16),
                          if (_recentScores.isEmpty)
                            const Card(
                              color: Color(0xFF121324),
                              child: Padding(
                                padding: EdgeInsets.all(16.0),
                                child: Center(
                                  child: Text(
                                    'No recent scores logged. Start saving workouts to track recovery.',
                                    style: TextStyle(color: Colors.grey),
                                  ),
                                ),
                              ),
                            )
                          else
                            ..._recentScores.map((scoreObj) {
                              final String dateStr = scoreObj['date'] ?? '';
                              final double val = (scoreObj['score'] as num?)?.toDouble() ?? 0.0;
                              return Card(
                                color: const Color(0xFF121324),
                                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                                margin: const EdgeInsets.only(bottom: 12),
                                child: ListTile(
                                  leading: Icon(
                                    Icons.healing_outlined,
                                    color: val >= 80 ? const Color(0xFF10B981) : const Color(0xFF6366F1),
                                  ),
                                  title: Text(
                                    'Date: $dateStr',
                                    style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                                  ),
                                  trailing: Text(
                                    '${val.toInt()}%',
                                    style: TextStyle(
                                      color: val >= 80 ? const Color(0xFF10B981) : const Color(0xFF6366F1),
                                      fontWeight: FontWeight.bold,
                                      fontSize: 16,
                                    ),
                                  ),
                                ),
                              );
                            }),
                        ],
                      ),
                    ),
            ],
          ),
        ),
      ),
    );
  }
}
