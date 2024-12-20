// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'health_metrics_model.dart';

// **************************************************************************
// TypeAdapterGenerator
// **************************************************************************

class HealthMetricsAdapter extends TypeAdapter<HealthMetrics> {
  @override
  final int typeId = 1;

  @override
  HealthMetrics read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return HealthMetrics(
      id: fields[0] as String,
      userId: fields[1] as String,
      heartRate: fields[2] as double,
      systolicPressure: fields[3] as double,
      diastolicPressure: fields[4] as double,
      exerciseMinutes: fields[5] as int,
      timestamp: fields[6] as DateTime,
      bloodPressure: fields[8] as String,
      notes: fields[7] as String?,
    );
  }

  @override
  void write(BinaryWriter writer, HealthMetrics obj) {
    writer
      ..writeByte(9)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.userId)
      ..writeByte(2)
      ..write(obj.heartRate)
      ..writeByte(3)
      ..write(obj.systolicPressure)
      ..writeByte(4)
      ..write(obj.diastolicPressure)
      ..writeByte(5)
      ..write(obj.exerciseMinutes)
      ..writeByte(6)
      ..write(obj.timestamp)
      ..writeByte(7)
      ..write(obj.notes)
      ..writeByte(8)
      ..write(obj.bloodPressure);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is HealthMetricsAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}
