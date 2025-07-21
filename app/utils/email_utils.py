# Email sending utility
import random
import smtplib
from email.mime.text import MIMEText
from typing import List

from fastapi import BackgroundTasks

from app.utils.logger import logger
import uuid
from datetime import datetime


def send_email(
    background_tasks: BackgroundTasks,
    subject: str,
    body: str,
    recipients: List[str],
    db,  # DynamoDB resource
):
    async def send():
        table = await db.Table("users")
        for recipient in recipients:
            email_id = str(uuid.uuid4())
            email_log = {
                'id': email_id,
                'recipient': recipient,
                'subject': subject,
                'body': body,
                'status': 'pending',
                'created_at': datetime.now().isoformat(),
            }
            table.put_item(Item=email_log)
            try:
                logger.info(f"Sending email to {recipient} with {subject} and {body}")
                # Simulate random failure (30% chance)
                if random.random() < 0.3:
                    raise Exception("Simulated email sending failure")
                # Simulate success
                table.update_item(
                    Key={'id': email_id},
                    UpdateExpression="set #s = :s, sent_at = :t",
                    ExpressionAttributeNames={'#s': 'status'},
                    ExpressionAttributeValues={':s': 'sent', ':t': datetime.now().isoformat()}
                )
                logger.info(f"Email sent successfully to {recipient}")
            except Exception as e:
                table.update_item(
                    Key={'id': email_id},
                    UpdateExpression="set #s = :s, failed_at = :t, error_message = :e",
                    ExpressionAttributeNames={'#s': 'status'},
                    ExpressionAttributeValues={
                        ':s': 'failed',
                        ':t': datetime.now().isoformat(),
                        ':e': str(e)
                    }
                )
                logger.error(f"Failed to send email to {recipient}: {str(e)}")

    background_tasks.add_task(send)
