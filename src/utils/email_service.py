import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText

# load env variables from .env file
load_dotenv()

def send_email(to_mail, subject, body):
    from_email = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT"))

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['from'] = from_email
    msg['To'] = to_mail

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(from_email, password)
            server.sendmail(from_email, to_mail, msg.as_string())
        print(f"Email successfully sent to {to_mail}")
    except Exception as e:
        print(f"Failed to send email to {to_mail}: {e}")