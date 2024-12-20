import 'package:hive/hive.dart';

part 'health_metrics_model.g.dart';

@HiveType(typeId: 1)
class HealthMetrics {
  @HiveField(0)
  final String id;

  @HiveField(1)
  final String userId;

  @HiveField(2)
  final double heartRate;

  @HiveField(3)
  final double systolicPressure;

  @HiveField(4)
  final double diastolicPressure;

  @HiveField(5)
  final int exerciseMinutes;

  @HiveField(6)
  final DateTime timestamp;

  @HiveField(7)
  final String? notes;

  @HiveField(8)
  final String bloodPressure;

  HealthMetrics({
    required this.id,
    required this.userId,
    required this.heartRate,
    required this.systolicPressure,
    required this.diastolicPressure,
    required this.exerciseMinutes,
    required this.timestamp,
    required this.bloodPressure,
    this.notes,
  });

  factory HealthMetrics.fromJson(Map<String, dynamic> json) {
    return HealthMetrics(
      id: json['id'],
      userId: json['user_id'],
      heartRate: json['heart_rate'].toDouble(),
      systolicPressure: json['systolic_pressure'].toDouble(),
      diastolicPressure: json['diastolic_pressure'].toDouble(),
      exerciseMinutes: json['exercise_minutes'],
      timestamp: DateTime.parse(json['timestamp']),
      bloodPressure: '${json['systolic_pressure']}/${json['diastolic_pressure']}',
      notes: json['notes'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'heart_rate': heartRate,
      'systolic_pressure': systolicPressure,
      'diastolic_pressure': diastolicPressure,
      'exercise_minutes': exerciseMinutes,
      'timestamp': timestamp.toIso8601String(),
      'blood_pressure': bloodPressure,
      'notes': notes,
    };
  }

  HealthMetrics copyWith({
    String? id,
    String? userId,
    double? heartRate,
    double? systolicPressure,
    double? diastolicPressure,
    int? exerciseMinutes,
    DateTime? timestamp,
    String? bloodPressure,
    String? notes,
  }) {
    return HealthMetrics(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      heartRate: heartRate ?? this.heartRate,
      systolicPressure: systolicPressure ?? this.systolicPressure,
      diastolicPressure: diastolicPressure ?? this.diastolicPressure,
      exerciseMinutes: exerciseMinutes ?? this.exerciseMinutes,
      timestamp: timestamp ?? this.timestamp,
      bloodPressure: bloodPressure ?? this.bloodPressure,
      notes: notes ?? this.notes,
    );
  }
}
