import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from chat import (
    initialize_chat_session,
    send_message_to_chatbot,
    update_user_data,
    update_health_metrics,
    set_reminder,
    detect_emergency,
    personalize_response,
    get_health_report,
    get_health_metrics_summary,
    health_metrics_tracker  # Import the tracker to access DataFrame
)
import logging
from notifications import notification_manager, TWILIO_AVAILABLE
import uuid

reminder_schedule = {} 

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Streamlit app
st.set_page_config(page_title="Cardio-Health Assistant", layout="wide")
st.title("Cardio-Health Assistant")
st.write("Welcome to the Cardio Health Bot! This tool helps manage cardiovascular health by tracking health metrics, setting reminders, and providing personalized advice.")

# Create tabs for different sections
tab1, tab2, tab3 = st.tabs(["Health Metrics", "Chat", "Health Report"])

# Add more visualization methods
def create_health_metrics_dashboard(metrics_df):
    """Create a comprehensive health metrics dashboard with multiple visualizations."""
    st.subheader("Health Metrics Visualization")
    
    # Ensure timestamp is datetime
    metrics_df['timestamp'] = pd.to_datetime(metrics_df['timestamp'])
    
    # Select visualization type
    viz_type = st.selectbox("Select Visualization Type", [
        "Time Series Trends", 
        "Distribution Analysis", 
        "Correlation Heatmap", 
        "Box Plot Comparison"
    ])
    
    # Metrics selection
    numeric_columns = [col for col in metrics_df.columns if col not in ['timestamp', 'blood_pressure']]
    selected_metrics = st.multiselect("Select Metrics", numeric_columns, default=numeric_columns[:3])
    
    if not selected_metrics:
        st.warning("Please select at least one metric to visualize.")
        return
    
    # Visualization logic based on selected type
    if viz_type == "Time Series Trends":
        # Interactive time series line chart
        fig = go.Figure()
        for metric in selected_metrics:
            fig.add_trace(go.Scatter(
                x=metrics_df['timestamp'], 
                y=metrics_df[metric], 
                mode='lines+markers', 
                name=metric
            ))
        fig.update_layout(
            title='Health Metrics Trends Over Time',
            xaxis_title='Date',
            yaxis_title='Value',
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    
    elif viz_type == "Distribution Analysis":
        # Kernel Density Estimation (KDE) plot
        fig = ff.create_distplot(
            [metrics_df[metric].dropna() for metric in selected_metrics],
            selected_metrics,
            show_hist=True,
            show_rug=False
        )
        fig.update_layout(
            title='Distribution of Health Metrics',
            xaxis_title='Value',
            yaxis_title='Density',
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    
    elif viz_type == "Correlation Heatmap":
        # Correlation heatmap
        corr_matrix = metrics_df[selected_metrics].corr()
        fig = px.imshow(
            corr_matrix, 
            text_auto=True, 
            aspect="auto", 
            title="Correlation Between Health Metrics"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    elif viz_type == "Box Plot Comparison":
        # Box plot for comparing metric distributions
        fig = go.Figure()
        for metric in selected_metrics:
            fig.add_trace(go.Box(y=metrics_df[metric], name=metric))
        
        fig.update_layout(
            title='Box Plot: Health Metrics Distribution',
            yaxis_title='Value',
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)

with tab1:
    st.header("Health Metrics Dashboard")
    
    # Display metrics summary
    metrics_summary = get_health_metrics_summary()
    
    if metrics_summary and not health_metrics_tracker.metrics_df.empty:
        # Existing metric cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            heart_rate_last = metrics_summary['heart_rate'].get('last', 'N/A')
            heart_rate_avg = metrics_summary['heart_rate'].get('average', 0)
            
            if isinstance(heart_rate_last, (int, float)):
                st.metric("Heart Rate", 
                          f"{heart_rate_last:.1f} BPM", 
                          f"{heart_rate_last - heart_rate_avg:.1f}")
            else:
                st.metric("Heart Rate", "N/A", "")
        
        with col2:
            st.metric("Blood Pressure", 
                      str(metrics_summary.get('blood_pressure', {}).get('last', 'N/A')), 
                      "")
        
        with col3:
            bmi_last = metrics_summary.get('bmi', {}).get('last', 'N/A')
            bmi_avg = metrics_summary.get('bmi', {}).get('average', 0)
            
            if isinstance(bmi_last, (int, float)):
                st.metric("BMI", 
                          f"{bmi_last:.1f}", 
                          f"{bmi_last - bmi_avg:.1f}")
            else:
                st.metric("BMI", "N/A", "")
        
        # New comprehensive visualization dashboard
        create_health_metrics_dashboard(health_metrics_tracker.metrics_df)
    
    else:
        st.warning("No health metrics recorded yet. Start tracking your health by entering metrics in the sidebar!")

    st.sidebar.title("User Profile and Health Metrics")

    # Collect user information
    st.sidebar.header("Personal Information")
    name = st.sidebar.text_input("Name")
    age = st.sidebar.number_input("Age", min_value=0, max_value=120)
    gender = st.sidebar.selectbox("Gender", ["", "Male", "Female", "Other"])

    # Health Metrics Input
    st.sidebar.header("Add Health Metrics")
    
    # Heart Rate
    heart_rate = st.sidebar.number_input("Heart Rate (BPM)", min_value=0, max_value=300, step=1)
    
    # Blood Pressure
    bp_systolic = st.sidebar.number_input("Blood Pressure (Systolic)", min_value=0, max_value=300, step=1)
    bp_diastolic = st.sidebar.number_input("Blood Pressure (Diastolic)", min_value=0, max_value=200, step=1)
    blood_pressure = f"{bp_systolic}/{bp_diastolic}"
    
    # Cholesterol
    cholesterol_total = st.sidebar.number_input("Total Cholesterol", min_value=0, max_value=500, step=1)
    cholesterol_ldl = st.sidebar.number_input("LDL Cholesterol", min_value=0, max_value=500, step=1)
    cholesterol_hdl = st.sidebar.number_input("HDL Cholesterol", min_value=0, max_value=500, step=1)
    
    # Blood Sugar
    blood_sugar = st.sidebar.number_input("Blood Sugar (mg/dL)", min_value=0, max_value=1000, step=1)
    
    # Weight and Height for BMI
    weight = st.sidebar.number_input("Weight (kg)", min_value=0.0, max_value=500.0, step=0.1)
    height = st.sidebar.number_input("Height (m)", min_value=0.0, max_value=3.0, step=0.01)
    
    # Exercise Minutes
    exercise_minutes = st.sidebar.number_input("Exercise Minutes", min_value=0, max_value=1440, step=1)
    
    # Submit Metrics Button
    if st.sidebar.button("Submit Health Metrics"):
        # Update health metrics
        update_health_metrics(
            'heart_rate', heart_rate,
            blood_pressure=blood_pressure,
            cholesterol_total=cholesterol_total,
            cholesterol_ldl=cholesterol_ldl,
            cholesterol_hdl=cholesterol_hdl,
            blood_sugar=blood_sugar,
            weight=weight,
            height=height,
            exercise_minutes=exercise_minutes
        )
        st.sidebar.success("Health metrics updated successfully!")

    # Reminders and Alerts
    st.sidebar.header("Reminders")
    medication_reminder = st.sidebar.checkbox("Medication Reminder")
    exercise_reminder = st.sidebar.checkbox("Exercise Reminder")

    # Medication Reminders
    st.sidebar.header("Medication Reminders")
    medication_name = st.sidebar.text_input("Medication Name")
    medication_dosage = st.sidebar.text_input("Dosage")
    reminder_frequency = st.sidebar.number_input("Reminder Frequency (hours)", min_value=1, max_value=24)
    
    # Contact Information for Reminders
    contact_method_options = ["Email"]
    if TWILIO_AVAILABLE:
        contact_method_options.append("SMS")
        contact_method_options.append("Both")

    contact_method = st.sidebar.selectbox("Reminder Method", contact_method_options)
    contact_info = st.sidebar.text_input(f"{contact_method} Address/Number")
    
    # Add Medication Reminder Button
    if st.sidebar.button("Add Medication Reminder"):
        if medication_name and medication_dosage and contact_info:
            # Generate a unique user ID (in a real app, this would come from user authentication)
            user_id = str(uuid.uuid4())
            
            # Add reminder to database
            reminder_id = notification_manager.add_medication_reminder(
                user_id, 
                medication_name, 
                medication_dosage, 
                reminder_frequency
            )
            
            # Send initial notification
            reminder_message = f"Reminder: Take {medication_name} ({medication_dosage})"
            
            if contact_method in ["Email", "Both"]:
                notification_manager.send_email_reminder(contact_info, "Medication Reminder", reminder_message)
            
            if contact_method in ["SMS", "Both"]:
                if not TWILIO_AVAILABLE:
                    st.sidebar.warning("Twilio module not installed. SMS notifications are unavailable.")
                else:
                    notification_manager.send_sms_reminder(contact_info, reminder_message)
            
            st.sidebar.success(f"Medication reminder set for {medication_name}")
        else:
            st.sidebar.error("Please fill in all medication reminder details")

with tab2:
    # Chat interface (existing code remains the same)
    st.header("AI Health Assistant")
    
    # Initialize chat session
    if 'chat_session' not in st.session_state:
        st.session_state.chat_session = initialize_chat_session()

    # Display chat messages
    for message in st.session_state.chat_session.history:
        with st.chat_message(message.role):
            st.markdown(message.parts[0].text)

    # Chat input
    user_input = st.chat_input("Ask me anything about your cardiovascular health")
    if user_input:
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)

        # Get AI response
        response = send_message_to_chatbot(st.session_state.chat_session, user_input)
        
        # Display AI response
        with st.chat_message("assistant"):
            st.markdown(response)

with tab3:
    # Health Report Section
    st.header("Comprehensive Health Report")
    
    # Generate and display health report
    health_report = get_health_report()
    st.text_area("Detailed Health Metrics Report", health_report, height=400)
    
    # Option to download report
    st.download_button(
        label="Download Health Report",
        data=health_report,
        file_name=f"health_report_{datetime.now().strftime('%Y%m%d')}.txt",
        mime="text/plain"
    )

# Emergency detection
emergency_alert = detect_emergency()
if emergency_alert:
    st.error(emergency_alert)

# Display user summary
if name and age:
    st.markdown(f"**User:** {name}, **Age:** {age}")
