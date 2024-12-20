import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user_model.dart';
import '../models/health_metrics_model.dart';
import '../services/auth_service.dart';
import '../services/api_service.dart';
import '../services/storage_service.dart';
import '../services/notification_service.dart';

class AppState extends ChangeNotifier {
  final AuthService _authService;
  final ApiService _apiService;
  final StorageService _storageService;
  final NotificationService _notificationService;
  
  User? _currentUser;
  List<HealthMetrics> _healthMetrics = [];
  bool _isLoading = false;
  bool _isOffline = false;

  AppState(SharedPreferences prefs)
      : _authService = AuthService(prefs),
        _apiService = ApiService(),
        _storageService = StorageService(),
        _notificationService = NotificationService();

  User? get currentUser => _currentUser;
  List<HealthMetrics> get healthMetrics => _healthMetrics;
  bool get isLoading => _isLoading;
  bool get isOffline => _isOffline;

  Future<void> initialize() async {
    _isLoading = true;
    notifyListeners();

    try {
      await _storageService.initialize();
      await _notificationService.initialize();
      await checkAuthStatus();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> checkAuthStatus() async {
    try {
      final user = await _authService.getCurrentUser();
      if (user != null) {
        _currentUser = user;
        await _loadHealthMetrics();
      } else {
        // Try to load user from local storage
        _currentUser = await _storageService.getUser();
        if (_currentUser != null) {
          _healthMetrics = await _storageService.getHealthMetrics();
          _isOffline = true;
        }
      }
    } catch (e) {
      // If API fails, try to load from local storage
      _currentUser = await _storageService.getUser();
      if (_currentUser != null) {
        _healthMetrics = await _storageService.getHealthMetrics();
        _isOffline = true;
      }
    }
    notifyListeners();
  }

  Future<void> login(String email, String password) async {
    _isLoading = true;
    notifyListeners();

    try {
      _currentUser = await _authService.login(email, password);
      await _storageService.saveUser(_currentUser!);
      await _loadHealthMetrics();
      _isOffline = false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> register({
    required String email,
    required String password,
    required String name,
    required int age,
    required String gender,
  }) async {
    _isLoading = true;
    notifyListeners();

    try {
      _currentUser = await _authService.register(
        email: email,
        password: password,
        name: name,
        age: age,
        gender: gender,
      );
      
      // Save user to local storage
      await _storageService.saveUser(_currentUser!);
      
      // Initialize empty health metrics for new user
      _healthMetrics = [];
      await _storageService.saveHealthMetrics(_healthMetrics);
      
      _isOffline = false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> logout() async {
    _isLoading = true;
    notifyListeners();

    try {
      await _authService.logout();
      await _storageService.clearAll();
      await _notificationService.cancelAllNotifications();
      _currentUser = null;
      _healthMetrics = [];
      _isOffline = false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> _loadHealthMetrics() async {
    if (_currentUser == null) return;

    try {
      _healthMetrics = await _apiService.getHealthMetrics(_currentUser!.id);
      await _storageService.saveHealthMetrics(_healthMetrics);
      _isOffline = false;
    } catch (e) {
      // If API fails, load from local storage
      _healthMetrics = await _storageService.getHealthMetrics();
      _isOffline = true;
    }
    notifyListeners();
  }

  Future<void> loadHealthMetrics(String userId) async {
    try {
      final metrics = await _apiService.getHealthMetrics(userId);
      _healthMetrics = metrics;
      notifyListeners();
    } catch (e) {
      print('Error loading health metrics: $e');
    }
  }

  Future<void> addHealthMetric(HealthMetrics metric) async {
    if (_currentUser == null) return;

    try {
      if (!_isOffline) {
        await _apiService.addHealthMetric(metric);
      }
      
      _healthMetrics.add(metric);
      await _storageService.saveHealthMetrics(_healthMetrics);
      
      notifyListeners();
    } catch (e) {
      print('Error adding health metric: $e');
      rethrow;
    }
  }

  Future<String?> sendMessage(String message) async {
    if (_currentUser == null) return null;
    try {
      final response = await _apiService.sendMessage(_currentUser!.id, message);
      return response;
    } catch (e) {
      print('Error sending message: $e');
      return null;
    }
  }

  Future<void> updateUserProfile(User updatedUser) async {
    if (_currentUser == null) return;

    try {
      if (!_isOffline) {
        await _apiService.updateUserProfile(updatedUser);
        _currentUser = updatedUser;
      }
      await _storageService.saveUser(updatedUser);
      notifyListeners();
    } catch (e) {
      print('Error updating user profile: $e');
      rethrow;
    }
  }

  Future<void> scheduleHealthMetricReminder({
    required String metricType,
    required TimeOfDay time,
  }) async {
    await _notificationService.scheduleHealthMetricReminder(
      id: metricType.hashCode,
      metricType: metricType,
      time: time,
    );
  }

  Future<void> scheduleExerciseReminder({
    required TimeOfDay time,
    required List<String> days,
  }) async {
    await _notificationService.scheduleExerciseReminder(
      id: 'exercise'.hashCode,
      time: time,
      days: days,
    );
  }

  Future<void> scheduleMedicationReminder({
    required String medicationName,
    required TimeOfDay time,
    required List<String> days,
  }) async {
    await _notificationService.scheduleMedicationReminder(
      id: medicationName.hashCode,
      medicationName: medicationName,
      time: time,
      days: days,
    );
  }
}
