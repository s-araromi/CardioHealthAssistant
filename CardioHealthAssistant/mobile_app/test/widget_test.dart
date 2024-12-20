// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:provider/provider.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:cardio_health_assistant/main.dart';
import 'package:cardio_health_assistant/providers/app_state.dart';
import 'package:cardio_health_assistant/models/user_model.dart';
import 'package:cardio_health_assistant/models/health_metrics_model.dart';

void main() {
  setUp(() async {
    // Initialize Hive for testing
    await Hive.initFlutter();
    
    // Register Hive Adapters
    if (!Hive.isAdapterRegistered(0)) {
      Hive.registerAdapter(UserAdapter());
    }
    if (!Hive.isAdapterRegistered(1)) {
      Hive.registerAdapter(HealthMetricsAdapter());
    }
    
    // Open test boxes
    await Hive.openBox<User>('user');
    await Hive.openBox<HealthMetrics>('health_metrics');
  });

  tearDown(() async {
    // Clean up Hive boxes after each test
    await Hive.deleteFromDisk();
  });

  testWidgets('App launches successfully', (WidgetTester tester) async {
    // Set up SharedPreferences
    SharedPreferences.setMockInitialValues({});
    final prefs = await SharedPreferences.getInstance();
    
    // Build our app and trigger a frame
    await tester.pumpWidget(
      ChangeNotifierProvider(
        create: (_) => AppState(prefs),
        child: const MyApp(),
      ),
    );

    // Wait for app to initialize
    await tester.pumpAndSettle();

    // Verify that the login screen is shown initially
    expect(find.text('CardioHealth Assistant'), findsOneWidget);
    expect(find.text('Login'), findsOneWidget);
  });
}
