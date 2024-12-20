import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/user_model.dart';
import '../models/health_metrics_model.dart';

class ApiService {
  static const String baseUrl = 'http://localhost:8000'; // Change this to your backend URL

  // User endpoints
  Future<User> getUserProfile(String userId) async {
    final response = await http.get(Uri.parse('$baseUrl/users/$userId'));
    if (response.statusCode == 200) {
      return User.fromJson(jsonDecode(response.body));
    }
    throw Exception('Failed to load user profile');
  }

  Future<void> updateUserProfile(User user) async {
    final response = await http.put(
      Uri.parse('$baseUrl/users/${user.id}'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(user.toJson()),
    );
    if (response.statusCode != 200) {
      throw Exception('Failed to update user profile');
    }
  }

  // Health metrics endpoints
  Future<List<HealthMetrics>> getHealthMetrics(String userId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/health-metrics/$userId'),
    );
    if (response.statusCode == 200) {
      List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => HealthMetrics.fromJson(json)).toList();
    }
    throw Exception('Failed to load health metrics');
  }

  Future<void> addHealthMetric(HealthMetrics metric) async {
    final response = await http.post(
      Uri.parse('$baseUrl/health-metrics'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(metric.toJson()),
    );
    if (response.statusCode != 201) {
      throw Exception('Failed to add health metric');
    }
  }

  // Chat endpoints
  Future<String> sendMessage(String userId, String message) async {
    final response = await http.post(
      Uri.parse('$baseUrl/chat'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'user_id': userId,
        'message': message,
      }),
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body)['response'];
    }
    throw Exception('Failed to send message');
  }
}
