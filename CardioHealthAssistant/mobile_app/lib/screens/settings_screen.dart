// ignore_for_file: library_private_types_in_public_api

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/app_state.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({Key? key}) : super(key: key);

  @override
  _SettingsScreenState createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  bool _healthMetricsReminders = true;
  bool _exerciseReminders = true;
  bool _medicationReminders = true;
  TimeOfDay _healthMetricsTime = const TimeOfDay(hour: 9, minute: 0);
  TimeOfDay _exerciseTime = const TimeOfDay(hour: 7, minute: 0);
  TimeOfDay _medicationTime = const TimeOfDay(hour: 8, minute: 0);
  final List<String> _exerciseDays = ['Monday', 'Wednesday', 'Friday'];
  final String _selectedMedication = '';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildReminderSection(),
            const Divider(height: 32),
            _buildNotificationSettings(),
            const Divider(height: 32),
            _buildOfflineSettings(),
          ],
        ),
      ),
    );
  }

  Widget _buildReminderSection() {
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
            _buildReminderTile(
              title: 'Health Metrics',
              subtitle: 'Daily reminder to record your health metrics',
              value: _healthMetricsReminders,
              onChanged: (value) {
                setState(() => _healthMetricsReminders = value ?? false);
                if (value ?? false) {
                  _scheduleHealthMetricReminder();
                }
              },
              onTap: () async {
                final time = await _selectTime(
                  context,
                  initialTime: _healthMetricsTime,
                );
                if (time != null) {
                  setState(() => _healthMetricsTime = time);
                  if (_healthMetricsReminders) {
                    _scheduleHealthMetricReminder();
                  }
                }
              },
            ),
            _buildReminderTile(
              title: 'Exercise',
              subtitle: 'Reminder for your exercise routine',
              value: _exerciseReminders,
              onChanged: (value) {
                setState(() => _exerciseReminders = value ?? false);
                if (value ?? false) {
                  _scheduleExerciseReminder();
                }
              },
              onTap: () async {
                final time = await _selectTime(
                  context,
                  initialTime: _exerciseTime,
                );
                if (time != null) {
                  setState(() => _exerciseTime = time);
                  if (_exerciseReminders) {
                    _scheduleExerciseReminder();
                  }
                }
              },
            ),
            _buildReminderTile(
              title: 'Medication',
              subtitle: 'Reminder to take your medication',
              value: _medicationReminders,
              onChanged: (value) {
                setState(() => _medicationReminders = value ?? false);
                if (value ?? false) {
                  _scheduleMedicationReminder();
                }
              },
              onTap: () async {
                final time = await _selectTime(
                  context,
                  initialTime: _medicationTime,
                );
                if (time != null) {
                  setState(() => _medicationTime = time);
                  if (_medicationReminders) {
                    _scheduleMedicationReminder();
                  }
                }
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildReminderTile({
    required String title,
    required String subtitle,
    required bool value,
    required ValueChanged<bool?> onChanged,
    required VoidCallback onTap,
  }) {
    return ListTile(
      title: Text(title),
      subtitle: Text(subtitle),
      trailing: Switch(
        value: value,
        onChanged: onChanged,
      ),
      onTap: onTap,
    );
  }

  Widget _buildNotificationSettings() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Notification Settings',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            ListTile(
              title: const Text('Health Tips'),
              subtitle: const Text('Receive daily health tips'),
              trailing: Switch(
                value: true,
                onChanged: (value) {
                  // TODO: Implement health tips notifications
                },
              ),
            ),
            ListTile(
              title: const Text('Progress Updates'),
              subtitle: const Text('Weekly progress summary'),
              trailing: Switch(
                value: true,
                onChanged: (value) {
                  // TODO: Implement progress updates
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildOfflineSettings() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Offline Settings',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Consumer<AppState>(
              builder: (context, appState, child) {
                return ListTile(
                  title: const Text('Offline Mode'),
                  subtitle: Text(
                    appState.isOffline
                        ? 'Currently working offline'
                        : 'Connected to server',
                  ),
                  trailing: Icon(
                    appState.isOffline ? Icons.cloud_off : Icons.cloud_done,
                    color: appState.isOffline ? Colors.red : Colors.green,
                  ),
                );
              },
            ),
            ListTile(
              title: const Text('Clear Offline Data'),
              subtitle: const Text('Delete all cached data'),
              trailing: IconButton(
                icon: const Icon(Icons.delete_outline),
                onPressed: () {
                  _showClearDataDialog();
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  Future<TimeOfDay?> _selectTime(
    BuildContext context, {
    required TimeOfDay initialTime,
  }) async {
    return showTimePicker(
      context: context,
      initialTime: initialTime,
    );
  }

  void _scheduleHealthMetricReminder() {
    final appState = Provider.of<AppState>(context, listen: false);
    appState.scheduleHealthMetricReminder(
      metricType: 'Blood Pressure',
      time: _healthMetricsTime,
    );
  }

  void _scheduleExerciseReminder() {
    final appState = Provider.of<AppState>(context, listen: false);
    appState.scheduleExerciseReminder(
      time: _exerciseTime,
      days: _exerciseDays,
    );
  }

  void _scheduleMedicationReminder() {
    if (_selectedMedication.isEmpty) return;

    final appState = Provider.of<AppState>(context, listen: false);
    appState.scheduleMedicationReminder(
      medicationName: _selectedMedication,
      time: _medicationTime,
      days: const [
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday',
        'Sunday'
      ],
    );
  }

  Future<void> _showClearDataDialog() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Clear Offline Data'),
        content: const Text(
          'Are you sure you want to clear all offline data? '
          'This action cannot be undone.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Clear'),
          ),
        ],
      ),
    );

    if (confirmed ?? false) {
      // ignore: use_build_context_synchronously
      Provider.of<AppState>(context, listen: false);
      // TODO: Implement clear offline data
    }
  }
}
