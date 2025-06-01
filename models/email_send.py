import sys
sys.path.append(r"C:\Users\unmes\Documents\RAGful_dev\meet_scheduler")

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from config import SMTP_CONFIG



def send_confirmation_email(
    recipient_emails,
    meeting_type,
    meeting_date,
    meeting_start_time,
    meeting_end_time,
    participants,
    purpose
):
    subject = f"Meeting Confirmation - {meeting_type.capitalize()} with {', '.join(participants)}"
    
    body = f"""Dear Participant,

This is to confirm your scheduled meeting:

Type: {meeting_type.capitalize()}
Date: {meeting_date}
Time: {meeting_start_time} - {meeting_end_time}
Participants: {', '.join(participants)}
Purpose: {purpose}

If you have any questions or need to reschedule, please contact us.

Thank you,
Meet Schedular
"""

    msg = MIMEMultipart()
    msg['From'] = SMTP_CONFIG["sender_email"]
    msg['To'] = ', '.join(recipient_emails)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_CONFIG["host"], SMTP_CONFIG["port"])
        server.starttls()
        server.login(SMTP_CONFIG["sender_email"], SMTP_CONFIG["password"])
        server.sendmail(SMTP_CONFIG["sender_email"], recipient_emails, msg.as_string())
        server.quit()
        print("Email sent successfully!")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
    

if __name__ == "__main__":
    recipient_emails = ["unmeshsupekar3@gmail.com"]
    send_confirmation_email(
        recipient_emails=recipient_emails,
        meeting_type="consultation",
        meeting_date="2025-06-10",
        meeting_start_time="14:00",
        meeting_end_time="14:30",
        participants=["Dr. Smith"],
        purpose="Health check-up"
    )