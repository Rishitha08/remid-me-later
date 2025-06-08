from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
from config import Config
from celery import Celery
import pytz

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db = SQLAlchemy(app)

# Initialize Celery
def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    return celery

celery = make_celery(app)

# Database Model with timezone support
class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), nullable=False)
    time = db.Column(db.String(8), nullable=False)
    message = db.Column(db.Text, nullable=False)
    reminder_method = db.Column(db.String(20), default='email')
    phone_number = db.Column(db.String(20), nullable=True)
    email_address = db.Column(db.String(100), nullable=True)
    is_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')))
    
    def to_dict(self):
        # Convert UTC to IST for display
        ist_timezone = pytz.timezone('Asia/Kolkata')
        if self.created_at.tzinfo is None:
            # If naive datetime, assume it's already in IST
            created_at_ist = self.created_at
        else:
            # If timezone-aware, convert to IST
            created_at_ist = self.created_at.astimezone(ist_timezone)
        
        return {
            'id': self.id,
            'date': self.date,
            'time': self.time,
            'message': self.message,
            'reminder_method': self.reminder_method,
            'phone_number': self.phone_number,
            'email_address': self.email_address,
            'is_sent': self.is_sent,
            'created_at': created_at_ist.isoformat()
        }
    
    def get_reminder_datetime(self):
        """Convert date and time strings to datetime object"""
        date_time_str = f"{self.date} {self.time}"
        return datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/reminder', methods=['POST'])
def create_reminder():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Extract and validate required fields
        date = data.get('date')
        time = data.get('time')
        message = data.get('message')
        reminder_method = data.get('reminder_method', 'email')
        phone_number = data.get('phone_number')
        email_address = data.get('email_address')
        
        if not all([date, time, message]):
            return jsonify({'error': 'Missing required fields: date, time, message'}), 400
        
        # Validate contact information based on method
        if reminder_method == 'sms' and not phone_number:
            return jsonify({'error': 'Phone number required for SMS reminders'}), 400
        
        if reminder_method == 'email' and not email_address:
            return jsonify({'error': 'Email address required for email reminders'}), 400
        
        # Validate date and time format
        try:
            datetime.strptime(date, '%Y-%m-%d')
            if len(time.split(':')) == 2:
                time = time + ':00'
            datetime.strptime(time, '%H:%M:%S')
        except ValueError:
            return jsonify({'error': 'Invalid date or time format'}), 400
        
        # Create reminder with IST timezone
        ist_timezone = pytz.timezone('Asia/Kolkata')
        current_time_ist = datetime.now(ist_timezone)
        
        reminder = Reminder(
            date=date,
            time=time,
            message=message,
            reminder_method=reminder_method,
            phone_number=phone_number,
            email_address=email_address,
            created_at=current_time_ist
        )
        
        db.session.add(reminder)
        db.session.commit()
        
        # Schedule the reminder
        from tasks import schedule_reminder
        schedule_reminder.delay(reminder.id)
        
        return jsonify({
            'message': 'Reminder created and scheduled successfully',
            'reminder': reminder.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/api/reminders', methods=['GET'])
def get_reminders():
    try:
        reminders = Reminder.query.order_by(Reminder.created_at.desc()).all()
        return jsonify({
            'reminders': [reminder.to_dict() for reminder in reminders]
        }), 200
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

# ADDED: Clear all reminders endpoint
@app.route('/api/reminders/clear', methods=['DELETE'])
def clear_all_reminders():
    try:
        # Get count before deletion for response
        reminder_count = Reminder.query.count()
        
        if reminder_count == 0:
            return jsonify({'message': 'No reminders to clear'}), 200
        
        # Delete all reminders
        Reminder.query.delete()
        db.session.commit()
        
        return jsonify({
            'message': f'Successfully cleared {reminder_count} reminders',
            'cleared_count': reminder_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
