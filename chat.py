# chat.py

import os
import logging
import google.generativeai as genai
from datetime import datetime, timedelta

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

# User data storage structures
user_preferences = {}  # Stores user-specific preferences and goals
user_data = {}  # Stores user health data like age, gender, etc.
reminder_schedule = {}  # Schedule for reminders
health_metrics = {}  # Dictionary to track health metrics like blood pressure, heart rate, etc.

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

def update_health_metrics(metric, value):
    """Update health metrics (e.g., blood pressure, heart rate) with given values."""
    health_metrics[metric] = value
    logging.info(f"Updated health metrics: {metric} = {value}")

def set_reminder(event, interval_minutes):
    """Set a reminder for a specified event with a recurring interval in minutes."""
    next_reminder = datetime.now() + timedelta(minutes=interval_minutes)
    reminder_schedule[event] = next_reminder
    logging.info(f"Reminder set for '{event}' at {next_reminder}")

def detect_emergency():
    """Check for critical conditions in health metrics and return emergency alerts."""
    emergency_alert = None
    if "blood_pressure" in health_metrics:
        systolic, diastolic = map(int, health_metrics["blood_pressure"].split("/"))
        if systolic >= 180 or diastolic >= 120:
            emergency_alert = "Your blood pressure is critically high. Please seek immediate medical attention!"
            logging.warning("Critical blood pressure detected.")
    if "heart_rate" in health_metrics and int(health_metrics["heart_rate"]) > 120:
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
