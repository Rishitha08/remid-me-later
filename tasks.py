from celery import Celery
from datetime import datetime, timedelta
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
from config import Config
import os
import sys
import pytz
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialize Celery
celery = Celery('tasks')
celery.config_from_object(Config)

@celery.task
def schedule_reminder(reminder_id):
    """Schedule a reminder to be sent at the specified time"""
    logger.info(f"📅 Scheduling reminder {reminder_id}")
    
    try:
        # Import here to avoid circular imports
        import app
        
        with app.app.app_context():
            reminder = app.db.session.get(app.Reminder, reminder_id)
            if not reminder:
                logger.error(f"❌ Reminder {reminder_id} not found")
                return f"Reminder {reminder_id} not found"
            
            # Calculate delay until reminder time
            reminder_datetime = reminder.get_reminder_datetime()
            current_time = datetime.now()
            
            logger.info(f"⏰ Reminder time: {reminder_datetime}, Current time: {current_time}")
            
            if reminder_datetime <= current_time:
                # Send immediately if time has passed
                logger.info(f"🚀 Sending reminder {reminder_id} immediately")
                send_reminder_now.delay(reminder_id)
            else:
                # Calculate delay in seconds
                delay = (reminder_datetime - current_time).total_seconds()
                logger.info(f"⏳ Scheduling reminder {reminder_id} with delay: {delay} seconds")
                
                # Schedule the reminder
                send_reminder_now.apply_async(args=[reminder_id], countdown=delay)
            
            return f"Reminder {reminder_id} scheduled successfully"
            
    except Exception as e:
        logger.error(f"❌ Error scheduling reminder {reminder_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error scheduling reminder {reminder_id}: {str(e)}"

@celery.task
def send_reminder_now(reminder_id):
    """Send the actual reminder via SMS or Email"""
    logger.info(f"📤 Sending reminder {reminder_id}")
    
    try:
        # Import here to avoid circular imports
        import app
        
        with app.app.app_context():
            reminder = app.db.session.get(app.Reminder, reminder_id)
            if not reminder:
                logger.error(f"❌ Reminder {reminder_id} not found")
                return f"Reminder {reminder_id} not found"
            
            if reminder.is_sent:
                logger.warning(f"⚠️ Reminder {reminder_id} already sent")
                return f"Reminder {reminder_id} already sent"
            
            logger.info(f"📋 Reminder details: Method={reminder.reminder_method}, Message={reminder.message[:50]}...")
            
            try:
                if reminder.reminder_method == 'sms':
                    logger.info(f"📱 Sending SMS to {reminder.phone_number}")
                    result = send_sms_reminder(reminder)
                elif reminder.reminder_method == 'email':
                    logger.info(f"📧 Sending email to {reminder.email_address}")
                    result = send_email_reminder(reminder)
                else:
                    error_msg = f"Unknown reminder method: {reminder.reminder_method}"
                    logger.error(f"❌ {error_msg}")
                    return error_msg
                
                # Mark as sent
                reminder.is_sent = True
                app.db.session.commit()
                
                logger.info(f"✅ Reminder {reminder_id} sent successfully: {result}")
                return result
                
            except Exception as e:
                logger.error(f"❌ Failed to send reminder {reminder_id}: {str(e)}")
                import traceback
                traceback.print_exc()
                return f"Failed to send reminder {reminder_id}: {str(e)}"
            
    except Exception as e:
        logger.error(f"❌ Error in send_reminder_now {reminder_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error in send_reminder_now {reminder_id}: {str(e)}"

def send_sms_reminder(reminder):
    """Send SMS reminder using Twilio"""
    logger.info("📱 Initializing SMS sending...")
    
    try:
        # Validate Twilio configuration
        if not all([Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN, Config.TWILIO_PHONE_NUMBER]):
            missing = []
            if not Config.TWILIO_ACCOUNT_SID: missing.append("TWILIO_ACCOUNT_SID")
            if not Config.TWILIO_AUTH_TOKEN: missing.append("TWILIO_AUTH_TOKEN")
            if not Config.TWILIO_PHONE_NUMBER: missing.append("TWILIO_PHONE_NUMBER")
            raise Exception(f"Missing Twilio credentials: {', '.join(missing)}")
        
        logger.info(f"🔑 Using Twilio Account SID: {Config.TWILIO_ACCOUNT_SID[:10]}...")
        logger.info(f"📞 From number: {Config.TWILIO_PHONE_NUMBER}")
        logger.info(f"📞 To number: {reminder.phone_number}")
        
        client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
        
        # Ensure phone numbers are in E.164 format
        from_number = Config.TWILIO_PHONE_NUMBER
        to_number = reminder.phone_number
        
        # Add country code if not present
        if not to_number.startswith('+'):
            to_number = '+91' + to_number  # Assuming Indian number
            logger.info(f"📞 Formatted to number: {to_number}")
        
        message_body = f"Reminder: {reminder.message}"
        logger.info(f"💬 Message: {message_body}")
        
        message = client.messages.create(
            body=message_body,
            from_=from_number,
            to=to_number
        )
        
        result = f"SMS sent successfully to {to_number}. SID: {message.sid}"
        logger.info(f"✅ {result}")
        return result
        
    except Exception as e:
        error_msg = f"Failed to send SMS: {str(e)}"
        logger.error(f"❌ {error_msg}")
        raise Exception(error_msg)

def send_email_reminder(reminder):
    """Send email reminder using SMTP"""
    logger.info("📧 Initializing email sending...")
    
    try:
        # Validate email configuration
        if not all([Config.EMAIL_ADDRESS, Config.EMAIL_PASSWORD, Config.SMTP_SERVER]):
            missing = []
            if not Config.EMAIL_ADDRESS: missing.append("EMAIL_ADDRESS")
            if not Config.EMAIL_PASSWORD: missing.append("EMAIL_PASSWORD")
            if not Config.SMTP_SERVER: missing.append("SMTP_SERVER")
            raise Exception(f"Missing email credentials: {', '.join(missing)}")
        
        logger.info(f"📧 From email: {Config.EMAIL_ADDRESS}")
        logger.info(f"📧 To email: {reminder.email_address}")
        logger.info(f"🌐 SMTP Server: {Config.SMTP_SERVER}:{Config.SMTP_PORT}")
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = Config.EMAIL_ADDRESS
        msg['To'] = reminder.email_address
        msg['Subject'] = "Reminder Notification"
        
        # Get current time in IST
        ist_timezone = pytz.timezone('Asia/Kolkata')
        current_time_ist = datetime.now(ist_timezone)
        
        body = f"""
        Hello!
        
        This is your scheduled reminder:
        
        {reminder.message}
        
        Reminder was set for: {reminder.date} at {reminder.time}
        Sent at: {current_time_ist.strftime('%Y-%m-%d %H:%M:%S IST')}
        
        Best regards,
        Remind Me Later App
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        logger.info("🔐 Connecting to SMTP server...")
        
        # Send email
        server = smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT)
        server.starttls()
        server.login(Config.EMAIL_ADDRESS, Config.EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(Config.EMAIL_ADDRESS, reminder.email_address, text)
        server.quit()
        
        result = f"Email sent successfully to {reminder.email_address}"
        logger.info(f"✅ {result}")
        return result
        
    except Exception as e:
        error_msg = f"Failed to send email: {str(e)}"
        logger.error(f"❌ {error_msg}")
        raise Exception(error_msg)

@celery.task
def check_pending_reminders():
    """Periodic task to check for any missed reminders"""
    logger.info("🔍 Checking for pending reminders...")
    
    try:
        import app
        
        with app.app.app_context():
            current_time = datetime.now()
            
            # Find reminders that should have been sent but weren't
            overdue_reminders = app.db.session.query(app.Reminder).filter(
                app.Reminder.is_sent == False,
                app.Reminder.date <= current_time.strftime('%Y-%m-%d'),
                app.Reminder.time <= current_time.strftime('%H:%M:%S')
            ).all()
            
            logger.info(f"📋 Found {len(overdue_reminders)} overdue reminders")
            
            for reminder in overdue_reminders:
                logger.info(f"🚀 Sending overdue reminder {reminder.id}")
                send_reminder_now.delay(reminder.id)
            
            return f"Checked {len(overdue_reminders)} overdue reminders"
            
    except Exception as e:
        logger.error(f"❌ Error checking pending reminders: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error checking pending reminders: {str(e)}"
