# app.py

import streamlit as st
from datetime import datetime, timedelta
from chat import (
    initialize_chat_session,
    send_message_to_chatbot,
    update_user_data,
    update_health_metrics,
    set_reminder,
    detect_emergency,
    personalize_response
)
import logging
reminder_schedule = {} 

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Streamlit app
st.set_page_config(page_title="Cardio-Health Assistant")
st.title("Cardio-Health Assistant")
st.write("Welcome to the Cardio Health Bot! This tool helps manage cardiovascular health by tracking health metrics, setting reminders, and providing personalized advice. It also monitors symptoms and offers lifestyle recommendations to support heart health.")

# Sidebar for User Profile and Health Metrics
st.sidebar.title("User Profile and Health Metrics")

# Collect user information
st.sidebar.subheader("User Information")
user_name = st.sidebar.text_input("Name:")
user_age = st.sidebar.number_input("Age:", min_value=1, max_value=120, step=1, format="%d")

# Collect health metrics
st.sidebar.subheader("Health Metrics")
blood_pressure = st.sidebar.text_input("Blood Pressure (e.g., 120/80):")
try:
    heart_rate = int(st.sidebar.text_input("Heart Rate (BPM):"))
    update_health_metrics("heart_rate", heart_rate)
except ValueError:
    st.sidebar.error("Please enter a valid heart rate (numeric value).")
exercise_minutes = st.sidebar.slider("Exercise Minutes Per Day:", min_value=0, max_value=120, step=1)

# Collect reminder preferences
st.sidebar.subheader("Reminders")
medication_reminder = st.sidebar.checkbox("Medication Reminder")
exercise_reminder = st.sidebar.checkbox("Exercise Reminder")

# Display user summary
if user_name and user_age:
    st.markdown(f"**User:** {user_name}, **Age:** {user_age}")
    update_user_data({"name": user_name, "age": user_age})

if blood_pressure:
    st.markdown(f"**Blood Pressure:** {blood_pressure}")
    update_health_metrics("blood_pressure", blood_pressure)
    emergency_alert = detect_emergency()  # Check for emergency situations
    if emergency_alert:
        st.write(f"Bot: {emergency_alert}")

if exercise_minutes > 0:
    st.markdown(f"**Exercise:** {exercise_minutes} mins/day")
    update_health_metrics("exercise_minutes", exercise_minutes)

# Set reminders
if medication_reminder:
    set_reminder("medication", 60)  # Example reminder every hour
    st.markdown("**Reminder:** Medication every hour")
if exercise_reminder:
    set_reminder("exercise", 720)  # Example reminder every 12 hours
    st.markdown("**Reminder:** Exercise every 12 hours")

# Initialize session state for chat history and chat session
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "chat_session" not in st.session_state:
    st.session_state.chat_session = initialize_chat_session(st.session_state.chat_history)

# Main chat interface
st.subheader("Chat with Cardio-Health Assistant")
user_input = st.text_input("Type your message here:")
if st.button("Send") and user_input:
    # Display user message
    st.write(f"You: {user_input}")
    
    # Process user input
    response = send_message_to_chatbot(st.session_state.chat_session, user_input)
    personalized_response = personalize_response(response)
    
    # Display bot response
    st.markdown(f"**Bot:** \n{personalized_response}")

    # Update chat history
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.session_state.chat_history.append({"role": "bot", "content": personalized_response})

# Display previous chat history
st.subheader("Chat History")
for message in st.session_state.chat_history:
    if message["role"] == "user":
        st.write(f"You: {message['content']}")
    else:
        st.write(f"Bot: {message['content']}")

# Reminder section
st.subheader("Reminders")
current_time = datetime.now()
for event, reminder_time in list(reminder_schedule.items()):
    if current_time >= reminder_time:
        st.write(f"Bot: Friendly reminder to {event}!")
        # Reschedule the reminder (e.g., for the next interval)
        reminder_schedule[event] = current_time + timedelta(minutes=60)
