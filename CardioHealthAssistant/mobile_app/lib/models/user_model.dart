import 'package:hive/hive.dart';

part 'user_model.g.dart';

@HiveType(typeId: 0)
class User {
  @HiveField(0)
  final String id;

  @HiveField(1)
  final String name;

  @HiveField(2)
  final String email;

  @HiveField(3)
  final int age;

  @HiveField(4)
  final String gender;

  @HiveField(5)
  final double weight;

  @HiveField(6)
  final double height;

  @HiveField(7)
  final String? profileImageUrl;

  User({
    required this.id,
    required this.name,
    required this.email,
    required this.age,
    required this.gender,
    required this.weight,
    required this.height,
    this.profileImageUrl,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      name: json['name'],
      email: json['email'],
      age: json['age'],
      gender: json['gender'],
      weight: json['weight'].toDouble(),
      height: json['height'].toDouble(),
      profileImageUrl: json['profile_image_url'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'email': email,
      'age': age,
      'gender': gender,
      'weight': weight,
      'height': height,
      'profile_image_url': profileImageUrl,
    };
  }

  User copyWith({
    String? id,
    String? name,
    String? email,
    int? age,
    String? gender,
    double? weight,
    double? height,
    String? profileImageUrl,
  }) {
    return User(
      id: id ?? this.id,
      name: name ?? this.name,
      email: email ?? this.email,
      age: age ?? this.age,
      gender: gender ?? this.gender,
      weight: weight ?? this.weight,
      height: height ?? this.height,
      profileImageUrl: profileImageUrl ?? this.profileImageUrl,
    );
  }
}
