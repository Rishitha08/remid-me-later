import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

def test_email():
    try:
        msg = MIMEMultipart()
        msg['From'] = Config.EMAIL_ADDRESS
        msg['To'] = "vncontacts0031@gmail.com"  # Send to yourself
        msg['Subject'] = "Test Reminder from Remind Me Later App"
        
        body = """
        Hello!
        
        This is a test reminder from your Remind Me Later app.
        
        If you're receiving this email, your email configuration is working correctly!
        
        Best regards,
        Remind Me Later App
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT)
        server.starttls()
        server.login(Config.EMAIL_ADDRESS, Config.EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(Config.EMAIL_ADDRESS, "vncontacts0031@gmail.com", text)
        server.quit()
        
        print("✅ Email sent successfully!")
        
    except Exception as e:
        print(f"❌ Email error: {e}")

if __name__ == "__main__":
    print("📧 Testing email functionality...")
    test_email()

