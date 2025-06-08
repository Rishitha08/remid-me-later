from twilio.rest import Client
from config import Config

def test_sms():
    try:
        client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
        
        message = client.messages.create(
            body='Test SMS from Remind Me Later app',
            from_=Config.TWILIO_PHONE_NUMBER,
            to='+919150952849'  # Your phone number
        )
        
        print(f"Message sent! SID: {message.sid}")
        print(f"Status: {message.status}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_sms()

