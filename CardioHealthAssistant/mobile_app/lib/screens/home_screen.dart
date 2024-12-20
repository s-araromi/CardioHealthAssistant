import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/app_state.dart';
import '../models/health_metrics_model.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  @override
  void initState() {
    super.initState();
    // Load health metrics when screen initializes
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final appState = Provider.of<AppState>(context, listen: false);
      if (appState.currentUser != null) {
        appState.loadHealthMetrics(appState.currentUser!.id);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Cardio Health Dashboard'),
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications),
            onPressed: () {
              // TODO: Show notifications
            },
          ),
        ],
      ),
      body: Consumer<AppState>(
        builder: (context, appState, child) {
          if (appState.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildHealthMetricsCard(appState),
                const SizedBox(height: 16),
                _buildRemindersCard(),
                const SizedBox(height: 16),
                _buildExerciseCard(appState),
              ],
            ),
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _showAddMetricDialog(context),
        child: const Icon(Icons.add),
      ),
    );
  }

  Widget _buildHealthMetricsCard(AppState appState) {
    final latestMetrics = appState.healthMetrics.isNotEmpty 
        ? appState.healthMetrics.last 
        : null;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Health Metrics',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            _buildMetricRow(
              icon: Icons.favorite,
              title: 'Heart Rate',
              value: latestMetrics != null ? '${latestMetrics.heartRate} BPM' : 'No data',
            ),
            const Divider(),
            _buildMetricRow(
              icon: Icons.speed,
              title: 'Blood Pressure',
              value: latestMetrics != null ? latestMetrics.bloodPressure : 'No data',
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRemindersCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Reminders',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            _buildReminderItem(
              title: 'Take medication',
              time: '08:00 AM',
            ),
            const Divider(),
            _buildReminderItem(
              title: 'Evening walk',
              time: '06:00 PM',
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildExerciseCard(AppState appState) {
    final latestMetrics = appState.healthMetrics.isNotEmpty 
        ? appState.healthMetrics.last 
        : null;
    
    final progress = latestMetrics != null 
        ? latestMetrics.exerciseMinutes / 45 // Assuming 45 minutes is the target
        : 0.0;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Exercise Progress',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            LinearProgressIndicator(
              value: progress,
              backgroundColor: Colors.red[100],
              valueColor: const AlwaysStoppedAnimation<Color>(Colors.red),
            ),
            const SizedBox(height: 8),
            Text(
              latestMetrics != null
                  ? '${latestMetrics.exerciseMinutes} minutes out of 45 minutes target'
                  : 'No exercise data available',
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMetricRow({
    required IconData icon,
    required String title,
    required String value,
  }) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Row(
          children: [
            Icon(icon, color: Colors.red),
            const SizedBox(width: 8),
            Text(title),
          ],
        ),
        Text(
          value,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  Widget _buildReminderItem({
    required String title,
    required String time,
  }) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(title),
        Text(
          time,
          style: const TextStyle(
            color: Colors.grey,
          ),
        ),
      ],
    );
  }

  void _showAddMetricDialog(BuildContext context) {
    final formKey = GlobalKey<FormState>();
    int? heartRate;
    String? bloodPressure;
    int? exerciseMinutes;

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Add Health Metrics'),
        content: Form(
          key: formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextFormField(
                decoration: const InputDecoration(labelText: 'Heart Rate (BPM)'),
                keyboardType: TextInputType.number,
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter heart rate';
                  }
                  return null;
                },
                onSaved: (value) => heartRate = int.tryParse(value ?? ''),
              ),
              TextFormField(
                decoration: const InputDecoration(labelText: 'Blood Pressure (e.g., 120/80)'),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter blood pressure';
                  }
                  return null;
                },
                onSaved: (value) => bloodPressure = value,
              ),
              TextFormField(
                decoration: const InputDecoration(labelText: 'Exercise Minutes'),
                keyboardType: TextInputType.number,
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter exercise minutes';
                  }
                  return null;
                },
                onSaved: (value) => exerciseMinutes = int.tryParse(value ?? ''),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              if (formKey.currentState?.validate() ?? false) {
                formKey.currentState?.save();
                final appState = Provider.of<AppState>(context, listen: false);
                if (appState.currentUser != null && 
                    heartRate != null && 
                    bloodPressure != null && 
                    exerciseMinutes != null) {
                  final metric = HealthMetrics(
                    id: DateTime.now().millisecondsSinceEpoch.toString(),
                    userId: appState.currentUser!.id,
                    heartRate: heartRate!.toDouble(),
                    systolicPressure: double.parse(bloodPressure!.split('/')[0]),
                    diastolicPressure: double.parse(bloodPressure!.split('/')[1]),
                    bloodPressure: bloodPressure!,
                    exerciseMinutes: exerciseMinutes!,
                    timestamp: DateTime.now(),
                  );
                  appState.addHealthMetric(metric);
                  Navigator.pop(context);
                }
              }
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }
}
