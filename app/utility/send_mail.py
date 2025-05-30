import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from decouple import config
from app.utility.caching import get_cache,set_cache
import logging

logger = logging.getLogger(__name__)


def send_email(recipient, subject, message):
    # Email configuration
    sender_email = config('SENDER_MAIL')
    receiver_email = recipient

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Attach the email body
    msg.attach(MIMEText(message, 'plain'))

    # Sending the email
    try:
        server = smtplib.SMTP(config('EMAIL_HOST'), config('EMAIL_PORT'))
        server.starttls()
        server.login(sender_email, config('EMAIL_HOST_PASSWORD'))
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
        
    except Exception as e:
        print(f"Failed to send email: {str(e)}")



def generate_otp():
    import random
    return random.randint(1000, 9999)


def send_otp(recipient):
    otp = generate_otp()
    send_email(recipient, 'OTP Verification', f'Your OTP is: {otp}, valid for 5 minutes')
    set_cache(recipient, otp, 300)

def verify_otp(recipient, otp):
    cached_otp = get_cache(recipient)
    print(f"cached otp: {cached_otp}")
    print(f"otp: {otp}")
    if int(otp) == int(cached_otp):
        return True
    elif cached_otp == None:
        return None
    return False






#send_email('paakwesinunoo135@gmail.com', 'Test Email', 'This is a test email from the Field Operations App')

