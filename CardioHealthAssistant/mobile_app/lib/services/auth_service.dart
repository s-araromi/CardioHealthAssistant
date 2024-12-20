import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user_model.dart';

class AuthService {
  static const String userKey = 'user_data';
  final SharedPreferences _prefs;

  AuthService(this._prefs);

  Future<User?> getCurrentUser() async {
    final userData = _prefs.getString(userKey);
    if (userData != null) {
      return User.fromJson(jsonDecode(userData));
    }
    return null;
  }

  Future<User> login(String email, String password) async {
    // Simulate network delay
    await Future.delayed(const Duration(seconds: 1));
    
    final userData = _prefs.getString(userKey);
    if (userData != null) {
      final user = User.fromJson(jsonDecode(userData));
      if (user.email == email) {
        return user;
      }
    }
    throw Exception('Invalid email or password');
  }

  Future<User> register({
    required String email,
    required String password,
    required String name,
    required int age,
    required String gender,
  }) async {
    // Simulate network delay
    await Future.delayed(const Duration(seconds: 1));
    
    final user = User(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      email: email,
      name: name,
      age: age,
      gender: gender,
    );
    
    await _prefs.setString(userKey, jsonEncode(user.toJson()));
    return user;
  }

  Future<void> logout() async {
    await _prefs.remove(userKey);
  }

  Future<bool> isAuthenticated() async {
    return _prefs.containsKey(userKey);
  }
}
