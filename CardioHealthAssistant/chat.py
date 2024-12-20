# chat.py

import os
import logging
import google.generativeai as genai
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pandas as pd
import numpy as np

# Load environment variables from .env file
load_dotenv()

# Configure API and logging
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Set up logging to capture interactions and errors
logging.basicConfig(filename='chatbot.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Model generation configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Safety settings
SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# Initialize the model with specialized cardiovascular instructions
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
    system_instruction=(
        """You are a specialized Cardiovascular Health Assistant, designed to help manage and monitor cardiovascular health. Your responses should be:
1. Medically informed but easily understandable
2. Always emphasize consulting healthcare providers for medical decisions
3. Focus on evidence-based lifestyle modifications and adherence
4. Alert users to emergency symptoms that require immediate medical attention
5. Track and analyze cardiovascular health metrics

Key areas of focus:
- Blood pressure monitoring
- Heart rate tracking
- Medication adherence
- Exercise recommendations
- Diet suggestions
- Stress management
- Risk factor identification
- Symptom monitoring"""
    ),
)

# Global health metrics storage
class HealthMetricsTracker:
    def __init__(self):
        self.metrics_df = pd.DataFrame(columns=[
            'timestamp', 
            'heart_rate', 
            'blood_pressure', 
            'cholesterol_total', 
            'cholesterol_ldl', 
            'cholesterol_hdl', 
            'blood_sugar', 
            'weight', 
            'height', 
            'bmi',
            'exercise_minutes'
        ])

    def add_metric(self, **kwargs):
        timestamp = datetime.now()
        new_entry = {'timestamp': timestamp}
        
        # Add all provided metrics
        for key, value in kwargs.items():
            new_entry[key] = value
        
        # Calculate BMI if weight and height are provided
        if 'weight' in kwargs and 'height' in kwargs:
            new_entry['bmi'] = self._calculate_bmi(kwargs['weight'], kwargs['height'])
        
        # Convert DataFrame to use _append method
        self.metrics_df = pd.concat([self.metrics_df, pd.DataFrame([new_entry])], ignore_index=True)
        logging.info(f"Added health metric: {new_entry}")

    def _calculate_bmi(self, weight, height):
        """Calculate BMI. Assumes weight in kg and height in meters."""
        return weight / (height ** 2)

    def get_metrics_summary(self):
        """Generate a summary of health metrics."""
        summary = {}
        for column in self.metrics_df.columns:
            if column != 'timestamp':
                summary[column] = {
                    'average': self.metrics_df[column].mean(),
                    'min': self.metrics_df[column].min(),
                    'max': self.metrics_df[column].max(),
                    'last': self.metrics_df[column].iloc[-1] if not self.metrics_df.empty else None
                }
        return summary

    def generate_health_report(self):
        """Generate a comprehensive health report with personalized recommendations."""
        summary = self.get_metrics_summary()
        
        report = "Comprehensive Health Metrics Report\n"
        report += f"Report Generated: {datetime.now()}\n\n"
        
        for metric, stats in summary.items():
            report += f"{metric.replace('_', ' ').title()}:\n"
            for stat_name, stat_value in stats.items():
                # Handle None or non-numeric values
                if stat_value is not None and isinstance(stat_value, (int, float)):
                    report += f"  {stat_name.title()}: {stat_value:.2f}\n"
                elif stat_value is not None:
                    report += f"  {stat_name.title()}: {stat_value}\n"
            report += "\n"
        
        # Add personalized recommendations
        report += generate_personalized_recommendations(summary)
        
        return report

def generate_personalized_recommendations(metrics_summary):
    """
    Generate personalized health recommendations based on user's metrics.
    
    Args:
        metrics_summary (dict): Summary of user's health metrics
    
    Returns:
        str: Personalized health recommendations
    """
    recommendations = []
    
    # Heart Rate Analysis
    if 'heart_rate' in metrics_summary:
        hr = metrics_summary['heart_rate'].get('last', None)
        if hr is not None:
            if hr < 60:
                recommendations.append("Your resting heart rate is low. Consider consulting a healthcare professional.")
            elif hr > 100:
                recommendations.append("Your resting heart rate is high. Focus on stress reduction and cardiovascular exercise.")
    
    # BMI Analysis
    if 'bmi' in metrics_summary:
        bmi = metrics_summary['bmi'].get('last', None)
        if bmi is not None:
            if bmi < 18.5:
                recommendations.append("You are underweight. Consult a nutritionist to develop a healthy weight gain plan.")
            elif bmi > 30:
                recommendations.append("Your BMI indicates obesity. Consider a comprehensive weight management program.")
    
    # Cholesterol Analysis
    if all(key in metrics_summary for key in ['cholesterol_total', 'cholesterol_hdl', 'cholesterol_ldl']):
        total_chol = metrics_summary['cholesterol_total'].get('last', None)
        hdl_chol = metrics_summary['cholesterol_hdl'].get('last', None)
        ldl_chol = metrics_summary['cholesterol_ldl'].get('last', None)
        
        if total_chol is not None and total_chol > 240:
            recommendations.append("Your total cholesterol is high. Consider dietary changes and consult your doctor.")
        
        if hdl_chol is not None and hdl_chol < 40:
            recommendations.append("Your HDL (good) cholesterol is low. Increase exercise and consider omega-3 rich foods.")
        
        if ldl_chol is not None and ldl_chol > 160:
            recommendations.append("Your LDL (bad) cholesterol is elevated. Discuss statin options with your healthcare provider.")
    
    # Blood Sugar Analysis
    if 'blood_sugar' in metrics_summary:
        blood_sugar = metrics_summary['blood_sugar'].get('last', None)
        if blood_sugar is not None and blood_sugar > 125:
            recommendations.append("Your blood sugar is high. Consider diabetes screening and lifestyle modifications.")
    
    # Exercise Analysis
    if 'exercise_minutes' in metrics_summary:
        exercise_mins = metrics_summary['exercise_minutes'].get('last', None)
        if exercise_mins is not None and exercise_mins < 150:
            recommendations.append("You're not meeting recommended weekly exercise. Aim for 150 minutes of moderate activity.")
    
    # Combine recommendations
    if recommendations:
        return "Personalized Health Recommendations:\n" + "\n".join(f"• {rec}" for rec in recommendations)
    else:
        return "No specific health recommendations at this time. Keep tracking your metrics!"

# Initialize global health metrics tracker
health_metrics_tracker = HealthMetricsTracker()

# User data storage structures
user_preferences = {}  # Stores user-specific preferences and goals
user_data = {}  # Stores user health data like age, gender, etc.
reminder_schedule = {}  # Schedule for reminders

def update_health_metrics(metric, value, **additional_metrics):
    """Update health metrics with additional context."""
    try:
        health_metrics_tracker.add_metric(**{metric: value, **additional_metrics})
        logging.info(f"Updated health metric: {metric} = {value}")
    except Exception as e:
        logging.error(f"Error updating health metrics: {e}")

def get_health_metrics_summary():
    """Retrieve health metrics summary."""
    return health_metrics_tracker.get_metrics_summary()

def get_health_report():
    """Retrieve generated health report."""
    return health_metrics_tracker.generate_health_report()

def initialize_chat_session(history=None):
    """Initialize a chat session with the specialized cardiovascular instructions."""
    return model.start_chat(history=history or [])

def send_message_to_chatbot(chat_session, user_input):
    """Send a user message to the chatbot and return the response."""
    response = chat_session.send_message(user_input)
    bot_response = response.candidates[0].content.parts[0].text.strip()  # Keep text with formatting
    logging.info(f"User: {user_input}")
    logging.info(f"Bot: {bot_response}")
    return bot_response

def update_user_data(data):
    """Update user data (e.g., age, gender) based on input."""
    user_data.update(data)
    logging.info(f"Updated user data: {user_data}")

def set_reminder(event, interval_minutes):
    """Set a reminder for a specified event with a recurring interval in minutes."""
    next_reminder = datetime.now() + timedelta(minutes=interval_minutes)
    reminder_schedule[event] = next_reminder
    logging.info(f"Reminder set for '{event}' at {next_reminder}")

def detect_emergency():
    """Check for critical conditions in health metrics and return emergency alerts."""
    emergency_alert = None
    if "blood_pressure" in user_data:
        systolic, diastolic = map(int, user_data["blood_pressure"].split("/"))
        if systolic >= 180 or diastolic >= 120:
            emergency_alert = "Your blood pressure is critically high. Please seek immediate medical attention!"
            logging.warning("Critical blood pressure detected.")
    if "heart_rate" in user_data and int(user_data["heart_rate"]) > 120:
        emergency_alert = "Your heart rate is unusually high. Consider seeing a healthcare provider if this persists."
        logging.warning("High heart rate detected.")
    return emergency_alert

def personalize_response(response):
    """Personalize the bot's response based on stored user preferences and data."""
    if "goal" in user_preferences:
        response += f"\n\nRemember, your goal is to {user_preferences['goal']}!"
    if "age" in user_data:
        response += f" Based on your age of {user_data['age']}, consider consulting your doctor for age-specific advice."
    return response
