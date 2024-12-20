import 'package:hive_flutter/hive_flutter.dart';
import '../models/user_model.dart';
import '../models/health_metrics_model.dart';

class StorageService {
  static const String userBoxName = 'user';
  static const String healthMetricsBoxName = 'health_metrics';

  Future<void> initialize() async {
    await Hive.initFlutter();
    
    // Register adapters
    if (!Hive.isAdapterRegistered(0)) {
      Hive.registerAdapter(UserAdapter());
    }
    if (!Hive.isAdapterRegistered(1)) {
      Hive.registerAdapter(HealthMetricsAdapter());
    }

    // Open boxes
    await Hive.openBox<User>(userBoxName);
    await Hive.openBox<HealthMetrics>(healthMetricsBoxName);
  }

  // User methods
  Future<void> saveUser(User user) async {
    final box = Hive.box<User>(userBoxName);
    await box.put('current_user', user);
  }

  Future<User?> getUser() async {
    final box = Hive.box<User>(userBoxName);
    return box.get('current_user');
  }

  Future<void> deleteUser() async {
    final box = Hive.box<User>(userBoxName);
    await box.delete('current_user');
  }

  // Health metrics methods
  Future<void> saveHealthMetrics(List<HealthMetrics> metrics) async {
    final box = Hive.box<HealthMetrics>(healthMetricsBoxName);
    await box.clear();
    await box.addAll(metrics);
  }

  Future<List<HealthMetrics>> getHealthMetrics() async {
    final box = Hive.box<HealthMetrics>(healthMetricsBoxName);
    return box.values.toList();
  }

  Future<void> addHealthMetric(HealthMetrics metric) async {
    final box = Hive.box<HealthMetrics>(healthMetricsBoxName);
    await box.add(metric);
  }

  Future<void> clearHealthMetrics() async {
    final box = Hive.box<HealthMetrics>(healthMetricsBoxName);
    await box.clear();
  }

  // General methods
  Future<void> clearAll() async {
    await Hive.box<User>(userBoxName).clear();
    await Hive.box<HealthMetrics>(healthMetricsBoxName).clear();
  }
}
