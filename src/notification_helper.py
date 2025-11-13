import logging
from enum import Enum
from typing import TYPE_CHECKING

from src.email_helper import EmailClient, send_email
from src.slack_helper import send_slack_message

if TYPE_CHECKING:
    from slack_sdk import WebClient

    from tests.test_utils import TestClient

logger = logging.getLogger("daily_learner")


class NotificationChannel(Enum):
    SLACK = "slack"
    EMAIL = "email"


def send_notification(
    channel_id: str | None,
    email: str | None,
    subject: str,
    message: str,
    notification_channel: NotificationChannel = NotificationChannel.SLACK,
    slack_client: "TestClient | None | WebClient" = None,
    email_client: EmailClient | None = None,
) -> bool:
    logger.info(
        f"Sending notification via {notification_channel.value} - {channel_id=}, {email=}"
    )

    if notification_channel is NotificationChannel.SLACK:
        if not channel_id:
            raise Exception(
                f"channel_id is required when notification_channel is {notification_channel.value}"
            )

        logger.info(f"Sending Slack notification to channel {channel_id}")
        try:
            send_slack_message(channel_id, message, slack_client)
            return True
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")

    if notification_channel is NotificationChannel.EMAIL:
        if not email:
            raise Exception(
                f"email is required when notification_channel is {notification_channel.value}"
            )

        logger.info(f"Sending email notification to {email}")
        try:
            send_email(email, subject, message, email_client)
            return True
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")

    return False
