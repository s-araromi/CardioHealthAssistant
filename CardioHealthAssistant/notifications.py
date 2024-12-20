import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import sqlite3
from datetime import datetime, timedelta
import logging
from dotenv import load_dotenv

# Optional imports
try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    logging.warning("Twilio module not installed. SMS notifications will be disabled.")

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    import pickle
    GOOGLE_CALENDAR_AVAILABLE = True
except ImportError:
    GOOGLE_CALENDAR_AVAILABLE = False
    logging.warning("Google Calendar libraries not installed. Calendar integration will be disabled.")

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='notifications.log')

class CalendarIntegration:
    def __init__(self):
        """
        Initialize Google Calendar integration with optional configuration.
        """
        # Check if Google Calendar integration is possible
        if not GOOGLE_CALENDAR_AVAILABLE:
            logging.warning("Google Calendar libraries not available.")
            self.service = None
            return

        # Paths for credentials and token
        self.SCOPES = ['https://www.googleapis.com/auth/calendar']
        self.CREDENTIALS_PATH = os.getenv('GOOGLE_CALENDAR_CREDENTIALS', 'credentials.json')
        self.TOKEN_PATH = 'token.pickle'

        # Try to get calendar service, but handle potential errors
        try:
            self.service = self._get_calendar_service()
        except Exception as e:
            logging.error(f"Failed to initialize Google Calendar service: {e}")
            self.service = None

    def _get_calendar_service(self):
        """
        Authenticate and create Google Calendar service with error handling.
        """
        # If Google Calendar libraries are not available, return None
        if not GOOGLE_CALENDAR_AVAILABLE:
            return None

        # Check if credentials file exists
        if not os.path.exists(self.CREDENTIALS_PATH):
            logging.warning(f"Google Calendar credentials file not found at {self.CREDENTIALS_PATH}")
            return None

        creds = None
        # The file token.pickle stores the user's access and refresh tokens
        if os.path.exists(self.TOKEN_PATH):
            try:
                with open(self.TOKEN_PATH, 'rb') as token:
                    creds = pickle.load(token)
            except Exception as e:
                logging.error(f"Error loading token: {e}")
                creds = None
        
        # If there are no (valid) credentials available, handle gracefully
        if not creds or not creds.valid:
            try:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.CREDENTIALS_PATH, self.SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open(self.TOKEN_PATH, 'wb') as token:
                    pickle.dump(creds, token)
            except Exception as e:
                logging.error(f"Failed to obtain Google Calendar credentials: {e}")
                return None

        return build('calendar', 'v3', credentials=creds)

    def create_health_event(self, title, description, start_time, end_time=None):
        """
        Create a health-related event in Google Calendar.
        Handles cases where service might not be available.
        """
        if not self.service:
            logging.warning("Google Calendar service not available. Cannot create event.")
            return None

        if end_time is None:
            end_time = start_time + timedelta(hours=1)
        
        event = {
            'summary': title,
            'description': description,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'UTC',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 30},
                    {'method': 'email', 'minutes': 60},
                ],
            },
        }

        try:
            event = self.service.events().insert(calendarId='primary', body=event).execute()
            logging.info(f"Event created: {event.get('htmlLink')}")
            return event
        except Exception as e:
            logging.error(f"Error creating calendar event: {e}")
            return None

    def list_upcoming_health_events(self, max_results=10):
        """
        List upcoming health-related events.
        Handles cases where service might not be available.
        """
        if not self.service:
            logging.warning("Google Calendar service not available. Cannot list events.")
            return []

        try:
            now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
            events_result = self.service.events().list(
                calendarId='primary', 
                timeMin=now,
                maxResults=max_results, 
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])
            
            return [
                {
                    'summary': event['summary'],
                    'start': event['start'].get('dateTime', event['start'].get('date')),
                    'description': event.get('description', '')
                } for event in events
            ]
        except Exception as e:
            logging.error(f"Error listing calendar events: {e}")
            return []

class NotificationManager:
    def __init__(self):
        # Email configuration
        self.email_sender = os.getenv('EMAIL_SENDER')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        
        # SMS configuration (Twilio)
        self.twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER')
        
        # SQLite database for tracking reminders
        self.conn = sqlite3.connect('reminders.db')
        self.create_tables()
        
        # Optional Calendar Integration
        try:
            self.calendar = CalendarIntegration()
        except Exception as e:
            logging.warning(f"Failed to initialize Calendar Integration: {e}")
            self.calendar = None

    def create_tables(self):
        """Create necessary database tables for reminder tracking."""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY,
                user_id TEXT,
                reminder_type TEXT,
                medication_name TEXT,
                dosage TEXT,
                frequency TEXT,
                last_taken DATETIME,
                next_reminder DATETIME,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        self.conn.commit()

    def add_medication_reminder(self, user_id, medication_name, dosage, frequency):
        """Add a new medication reminder."""
        cursor = self.conn.cursor()
        next_reminder = datetime.now() + timedelta(hours=frequency)
        
        cursor.execute('''
            INSERT INTO reminders 
            (user_id, reminder_type, medication_name, dosage, frequency, last_taken, next_reminder) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, 'medication', medication_name, dosage, frequency, None, next_reminder))
        
        self.conn.commit()
        logging.info(f"Added medication reminder for {medication_name}")
        return cursor.lastrowid

    def send_email_reminder(self, recipient_email, subject, message):
        """Send email reminder."""
        try:
            # Create a secure SSL context
            context = ssl.create_default_context()

            # Create the email message
            email_message = MIMEMultipart()
            email_message['From'] = self.email_sender
            email_message['To'] = recipient_email
            email_message['Subject'] = subject

            # Attach the message body
            email_message.attach(MIMEText(message, 'plain'))

            # Send the email
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
                server.login(self.email_sender, self.email_password)
                server.sendmail(self.email_sender, recipient_email, email_message.as_string())
            
            logging.info(f"Email reminder sent to {recipient_email}")
            return True
        except Exception as e:
            logging.error(f"Failed to send email: {e}")
            return False

    def send_sms_reminder(self, phone_number, message):
        """Send SMS reminder using Twilio."""
        if not TWILIO_AVAILABLE:
            logging.warning("Twilio module not installed. SMS notifications will be disabled.")
            return False
        
        try:
            client = Client(self.twilio_account_sid, self.twilio_auth_token)
            
            message = client.messages.create(
                body=message,
                from_=self.twilio_phone_number,
                to=phone_number
            )
            
            logging.info(f"SMS reminder sent to {phone_number}")
            return True
        except Exception as e:
            logging.error(f"Failed to send SMS: {e}")
            return False

    def get_upcoming_reminders(self, user_id):
        """Retrieve upcoming reminders for a user."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM reminders 
            WHERE user_id = ? AND is_active = 1 AND next_reminder <= ?
        ''', (user_id, datetime.now() + timedelta(days=1)))
        
        return cursor.fetchall()

    def mark_reminder_completed(self, reminder_id):
        """Mark a reminder as completed and update next reminder time."""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE reminders 
            SET last_taken = ?, next_reminder = ? 
            WHERE id = ?
        ''', (datetime.now(), datetime.now() + timedelta(hours=24), reminder_id))
        
        self.conn.commit()
        logging.info(f"Marked reminder {reminder_id} as completed")

    def schedule_health_reminder(self, title, description, start_time, end_time=None):
        """
        Schedule a comprehensive health reminder across multiple channels.
        
        :param title: Reminder title
        :param description: Reminder description
        :param start_time: Scheduled time for reminder
        :param end_time: Optional end time
        :return: Reminder details
        """
        # Create calendar event
        if self.calendar:
            calendar_event = self.calendar.create_health_event(title, description, start_time, end_time)
        else:
            logging.warning("Google Calendar service not available. Skipping calendar event creation.")
            calendar_event = None
        
        # You could add additional notification logic here
        # For example, send email/SMS reminders based on calendar event
        
        return calendar_event

    def close_connection(self):
        """Close database connection."""
        self.conn.close()

# Global notification manager instance
notification_manager = NotificationManager()
