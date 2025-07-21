# Email sending utility
import smtplib
from email.mime.text import MIMEText
from typing import List

from fastapi import BackgroundTasks


def send_email(background_tasks: BackgroundTasks, subject: str, body: str, recipients: List[str]):
    def send():
        # Dummy SMTP logic (replace with real credentials and server)
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = "noreply@example.com"
        msg["To"] = ", ".join(recipients)
        # Example: with smtplib.SMTP("localhost") as server:
        #     server.sendmail(msg["From"], recipients, msg.as_string())
        pass
    background_tasks.add_task(send)
