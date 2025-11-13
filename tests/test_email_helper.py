import smtplib
from unittest.mock import MagicMock, patch

import pytest

import src.secrets_manager
from src.email_helper import _markdown_to_html, send_email


class MockEmailClient:
    def __init__(self, should_fail=False):
        self.should_fail = should_fail
        self.sent_messages = []

    def sendmail(self, from_addr: str, to_addrs: list[str], msg: str) -> dict:
        if self.should_fail:
            raise Exception("Failed to send email")
        self.sent_messages.append({"from": from_addr, "to": to_addrs, "msg": msg})
        return {}

    def quit(self) -> None:
        pass


class TestSendEmail:
    def setup_method(self, method):
        class MockSecretsManager:
            def get_secret(self, key: str) -> str:
                secrets = {
                    "SMTP_FROM_EMAIL": "test@example.com",
                    "SMTP_SERVER": "smtp.example.com",
                    "SMTP_PORT": "587",
                    "SMTP_USERNAME": "testuser",
                    "SMTP_PASSWORD": "testpass",
                }
                return secrets.get(key, "")

        src.secrets_manager._secrets_manager = MockSecretsManager()

    def teardown_method(self, method):
        src.secrets_manager._secrets_manager = None

    @pytest.mark.parametrize(
        "recipient, subject, message, exception_string",
        [
            ("", "Test Subject", "Test Message", "Missing required arguments"),
            (
                "test@example.com",
                "",
                "Test Message",
                "Missing required arguments",
            ),
            (
                "test@example.com",
                "Test Subject",
                "",
                "Missing required arguments",
            ),
        ],
    )
    def test_send_email_with_missing_arguments_should_raise_exception(
        self, recipient, subject, message, exception_string
    ):
        with pytest.raises(Exception) as exception:
            send_email(recipient, subject, message, MockEmailClient())
        assert exception_string in str(exception.value)

    def test_send_email_with_valid_arguments_should_succeed(self):
        mock_client = MockEmailClient()
        result = send_email(
            recipient="test@example.com",
            subject="Test Subject",
            message="Test Message",
            client=mock_client,
        )

        assert result is True
        assert len(mock_client.sent_messages) == 1
        assert mock_client.sent_messages[0]["to"] == ["test@example.com"]

    def test_send_email_with_failing_client_should_raise_exception(self):
        mock_client = MockEmailClient(should_fail=True)
        with pytest.raises(Exception) as exception:
            send_email(
                recipient="test@example.com",
                subject="Test Subject",
                message="Test Message",
                client=mock_client,
            )
        assert "Error sending email" in str(exception.value)

    def test_send_email_without_client_should_use_smtp(self):
        with patch("smtplib.SMTP") as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server

            result = send_email(
                recipient="test@example.com",
                subject="Test Subject",
                message="Test Message",
            )

            assert result is True
            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once_with("testuser", "testpass")
            mock_server.sendmail.assert_called_once()

    def test_send_email_smtp_connection_failure_should_raise_exception(self):
        with patch("smtplib.SMTP") as mock_smtp:
            mock_smtp.side_effect = smtplib.SMTPException("Connection failed")

            with pytest.raises(Exception) as exception:
                send_email(
                    recipient="test@example.com",
                    subject="Test Subject",
                    message="Test Message",
                )
            assert "Error sending email" in str(exception.value)

    def test_send_email_includes_both_plain_and_html_parts(self):
        mock_client = MockEmailClient()
        send_email(
            recipient="test@example.com",
            subject="Test Subject",
            message="Test Message",
            client=mock_client,
        )

        assert len(mock_client.sent_messages) == 1
        msg = mock_client.sent_messages[0]["msg"]
        assert "Content-Type: text/plain" in msg
        assert "Content-Type: text/html" in msg

    def test_send_email_missing_smtp_from_email_should_raise_exception(self):
        class MockSecretsManagerNoFromEmail:
            def get_secret(self, key: str) -> str:
                if key == "SMTP_FROM_EMAIL":
                    return ""
                secrets = {
                    "SMTP_SERVER": "smtp.example.com",
                    "SMTP_PORT": "587",
                    "SMTP_USERNAME": "testuser",
                    "SMTP_PASSWORD": "testpass",
                }
                return secrets.get(key, "")

        src.secrets_manager._secrets_manager = MockSecretsManagerNoFromEmail()

        with pytest.raises(Exception) as exception:
            send_email(
                recipient="test@example.com",
                subject="Test Subject",
                message="Test Message",
                client=MockEmailClient(),
            )
        assert "SMTP_FROM_EMAIL secret not configured" in str(exception.value)

    def test_send_email_missing_smtp_server_should_raise_exception(self):
        class MockSecretsManagerNoServer:
            def get_secret(self, key: str) -> str:
                if key == "SMTP_SERVER":
                    return ""
                secrets = {
                    "SMTP_FROM_EMAIL": "test@example.com",
                    "SMTP_PORT": "587",
                    "SMTP_USERNAME": "testuser",
                    "SMTP_PASSWORD": "testpass",
                }
                return secrets.get(key, "")

        src.secrets_manager._secrets_manager = MockSecretsManagerNoServer()

        with pytest.raises(Exception) as exception:
            send_email(
                recipient="test@example.com",
                subject="Test Subject",
                message="Test Message",
            )
        assert "SMTP_SERVER secret not configured" in str(exception.value)

    def test_send_email_missing_smtp_port_should_raise_exception(self):
        class MockSecretsManagerNoPort:
            def get_secret(self, key: str) -> str:
                if key == "SMTP_PORT":
                    return ""
                secrets = {
                    "SMTP_FROM_EMAIL": "test@example.com",
                    "SMTP_SERVER": "smtp.example.com",
                    "SMTP_USERNAME": "testuser",
                    "SMTP_PASSWORD": "testpass",
                }
                return secrets.get(key, "")

        src.secrets_manager._secrets_manager = MockSecretsManagerNoPort()

        with pytest.raises(Exception) as exception:
            send_email(
                recipient="test@example.com",
                subject="Test Subject",
                message="Test Message",
            )
        assert "SMTP_PORT secret not configured" in str(exception.value)

    def test_send_email_missing_smtp_username_should_raise_exception(self):
        class MockSecretsManagerNoUsername:
            def get_secret(self, key: str) -> str:
                if key == "SMTP_USERNAME":
                    return ""
                secrets = {
                    "SMTP_FROM_EMAIL": "test@example.com",
                    "SMTP_SERVER": "smtp.example.com",
                    "SMTP_PORT": "587",
                    "SMTP_PASSWORD": "testpass",
                }
                return secrets.get(key, "")

        src.secrets_manager._secrets_manager = MockSecretsManagerNoUsername()

        with pytest.raises(Exception) as exception:
            send_email(
                recipient="test@example.com",
                subject="Test Subject",
                message="Test Message",
            )
        assert "SMTP_USERNAME secret not configured" in str(exception.value)

    def test_send_email_missing_smtp_password_should_raise_exception(self):
        class MockSecretsManagerNoPassword:
            def get_secret(self, key: str) -> str:
                if key == "SMTP_PASSWORD":
                    return ""
                secrets = {
                    "SMTP_FROM_EMAIL": "test@example.com",
                    "SMTP_SERVER": "smtp.example.com",
                    "SMTP_PORT": "587",
                    "SMTP_USERNAME": "testuser",
                }
                return secrets.get(key, "")

        src.secrets_manager._secrets_manager = MockSecretsManagerNoPassword()

        with pytest.raises(Exception) as exception:
            send_email(
                recipient="test@example.com",
                subject="Test Subject",
                message="Test Message",
            )
        assert "SMTP_PASSWORD secret not configured" in str(exception.value)


class TestMarkdownToHtml:
    def test_empty_message_should_raise_exception(self):
        with pytest.raises(Exception) as exception:
            _markdown_to_html("")
        assert str(exception.value) == "Empty message given"

    @pytest.mark.parametrize(
        "markdown, expected_html_content",
        [
            ("**bold text**", "<strong>bold text</strong>"),
            ("__bold text__", "<strong>bold text</strong>"),
            ("*italic text*", "<em>italic text</em>"),
            ("_italic text_", "<em>italic text</em>"),
            ("Simple text", "Simple text"),
            (
                "**bold** and *italic*",
                "<strong>bold</strong> and <em>italic</em>",
            ),
        ],
    )
    def test_markdown_conversion_to_html(self, markdown, expected_html_content):
        result = _markdown_to_html(markdown)
        assert expected_html_content in result
        assert "<html>" in result
        assert "<body" in result

    def test_line_breaks_are_converted_to_paragraphs(self):
        result = _markdown_to_html("Line 1\nLine 2\n\nLine 3")
        assert "<p>" in result
        assert "</p>" in result

    def test_html_output_includes_proper_structure(self):
        result = _markdown_to_html("Test message")
        assert result.strip().startswith("<html>")
        assert "</html>" in result
        assert "<body" in result
        assert "</body>" in result
