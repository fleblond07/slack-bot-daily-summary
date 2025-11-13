from unittest.mock import patch

import pytest

from src.notification_helper import NotificationChannel, send_notification
from tests.test_email_helper import MockEmailClient
from tests.test_utils import TestClient


class TestNotificationChannel:
    def test_notification_channel_values(self):
        assert NotificationChannel.SLACK.value == "slack"
        assert NotificationChannel.EMAIL.value == "email"


class TestSendNotification:
    def test_send_notification_via_slack_only(self):
        with patch("src.notification_helper.send_slack_message") as mock_slack:
            mock_slack.return_value = True
            test_client = TestClient()

            result = send_notification(
                channel_id="123456",
                email=None,
                subject="Test Subject",
                message="Test Message",
                notification_channel=NotificationChannel.SLACK,
                slack_client=test_client,
            )

            assert result is True
            assert mock_slack.call_count == 1
            call_args = mock_slack.call_args[0]
            assert call_args[0] == "123456"
            assert call_args[1] == "Test Message"
            assert call_args[2] is not None

    def test_send_notification_via_email_only(self):
        with patch("src.notification_helper.send_email") as mock_email:
            mock_email.return_value = True
            mock_email_client = MockEmailClient()

            result = send_notification(
                channel_id=None,
                email="test@example.com",
                subject="Test Subject",
                message="Test Message",
                notification_channel=NotificationChannel.EMAIL,
                email_client=mock_email_client,
            )

            assert result is True
            mock_email.assert_called_once_with(
                "test@example.com", "Test Subject", "Test Message", mock_email_client
            )

    def test_send_notification_slack_missing_channel_id_raises_exception(self):
        with pytest.raises(Exception) as exception:
            send_notification(
                channel_id=None,
                email=None,
                subject="Test Subject",
                message="Test Message",
                notification_channel=NotificationChannel.SLACK,
            )
        assert "channel_id is required" in str(exception.value)

    def test_send_notification_email_missing_email_raises_exception(self):
        with pytest.raises(Exception) as exception:
            send_notification(
                channel_id=None,
                email=None,
                subject="Test Subject",
                message="Test Message",
                notification_channel=NotificationChannel.EMAIL,
            )
        assert "email is required" in str(exception.value)

    def test_send_notification_slack_failure_returns_false(self):
        with patch("src.notification_helper.send_slack_message") as mock_slack:
            mock_slack.side_effect = Exception("Slack error")

            result = send_notification(
                channel_id="123456",
                email=None,
                subject="Test Subject",
                message="Test Message",
                notification_channel=NotificationChannel.SLACK,
                slack_client=TestClient(),
            )

            assert result is False

    def test_send_notification_email_failure_returns_false(self):
        with patch("src.notification_helper.send_email") as mock_email:
            mock_email.side_effect = Exception("Email error")
            mock_email_client = MockEmailClient()

            result = send_notification(
                channel_id=None,
                email="test@example.com",
                subject="Test Subject",
                message="Test Message",
                notification_channel=NotificationChannel.EMAIL,
                email_client=mock_email_client,
            )

            assert result is False

    def test_send_notification_defaults_to_slack(self):
        with patch("src.notification_helper.send_slack_message") as mock_slack:
            mock_slack.return_value = True

            result = send_notification(
                channel_id="123456",
                email=None,
                subject="Test Subject",
                message="Test Message",
                slack_client=TestClient(),
            )

            assert result is True
            mock_slack.assert_called_once()
