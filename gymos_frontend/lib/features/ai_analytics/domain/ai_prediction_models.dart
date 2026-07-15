class AiPredictionRequest {
  final double sleepHours;
  final int stressLevel;
  final int sorenessLevel;

  const AiPredictionRequest({
    required this.sleepHours,
    required this.stressLevel,
    required this.sorenessLevel,
  });

  Map<String, dynamic> toJson() {
    return {
      'sleep_hours': sleepHours,
      'stress_level': stressLevel,
      'soreness_level': sorenessLevel,
      'previous_scores': <double>[80.0, 85.0],
    };
  }
}

class AiPredictionResponse {
  final double readinessScore;
  final String insightText;
  final Map<String, dynamic> efficiencyData;

  const AiPredictionResponse({
    required this.readinessScore,
    required this.insightText,
    required this.efficiencyData,
  });

  factory AiPredictionResponse.fromJson(Map<String, dynamic> json) {
    // Map either forecasted_score (FastAPI recovery forecast response) or fallback fields
    final double score = (json['forecasted_score'] ?? json['readinessScore'] ?? 85.0).toDouble();
    final String text = json['description'] ?? json['insightText'] ?? '';
    final Map<String, dynamic> data = json['efficiencyData'] ?? <String, dynamic>{};

    return AiPredictionResponse(
      readinessScore: score,
      insightText: text,
      efficiencyData: data,
    );
  }
}
