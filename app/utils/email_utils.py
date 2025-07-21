# Email sending utility
import smtplib
from email.mime.text import MIMEText
from typing import List

from fastapi import BackgroundTasks

from app.utils.logger import logger


def send_email(background_tasks: BackgroundTasks, subject: str, body: str, recipients: List[str]):
    def send():
        logger.info(f"Sending email to {", ".join(recipients)} with {subject} and {body}")
    background_tasks.add_task(send)
