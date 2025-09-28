import pytest
from slack_sdk.errors import SlackApiError
import os
import time
import hmac
import hashlib
from src.slack_helper import (
    create_channel,
    send_slack_message,
    get_channel_id,
    _markdown_to_slackdown,
    verify_slack_request,
)
from tests.test_utils import TestClient
from unittest.mock import patch


class TestSendSlackMessage:
    @pytest.mark.parametrize(
        "channel_id, message, exception_string",
        [
            ("", "TestMessage", "Wrong argument given  - TestMessage"),
            ("123456", "", "Wrong argument given 123456 - "),
        ],
    )
    def test_slack_message_with_wrong_argument_should_raise_exception(
        self, channel_id, message, exception_string
    ):
        with pytest.raises(Exception) as exception:
            send_slack_message(channel_id, message, TestClient())
        assert str(exception.value) == exception_string

    def test_send_correct_slack_message(self):
        assert send_slack_message("123456", "TestMessage", TestClient()) is True

    def test_slack_exception_should_raise_exception(self):
        with pytest.raises(Exception):
            with patch("slack_sdk.WebClient.chat_postMessage") as patched:
                patched.side_effect = SlackApiError(
                    message="Something didnt go well",
                    response={"error": "This didnt go well"},
                )
                send_slack_message(channel_id="123", message="456")


class TestSlackGetChannel:
    def test_get_channel_with_empty_book_name_should_raise_exception(self):
        with pytest.raises(Exception) as exception:
            get_channel_id(object_name="", client=TestClient())
        assert str(exception.value) == "Empty object name given"

    def test_get_existing_channel_should_return_correct_id(self):
        assert get_channel_id(object_name="tata", client=TestClient()) == "123456"

    def test_get_non_existing_channel_should_create_channel(self):
        with patch("src.slack_helper.create_channel") as mock_create_channel:
            mock_create_channel.return_value = "890123"
            assert get_channel_id(object_name="Titi", client=TestClient()) == "890123"

            mock_create_channel.assert_called_once_with("titi")

    def test_slack_exception_should_raise_exception(self):
        with pytest.raises(Exception):
            with patch("src.slack_helper.create_channel") as patched:
                patched.side_effect = SlackApiError(
                    message="Something didnt go well",
                    response={"error": "This didnt go well"},
                )
                get_channel_id(object_name="123", client=TestClient())


class TestSlackCreateChannel:
    def test_create_channel_with_empty_book_name_should_raise_exception(self):
        with pytest.raises(Exception) as exception:
            create_channel(book_name="", client=TestClient())
        assert str(exception.value) == "Empty book name given"

    def test_create_channel_should_return_an_id(self):
        assert create_channel(book_name="Tata", client=TestClient()) == "123456"

    def test_slack_exception_should_raise_exception(self):
        with pytest.raises(Exception):
            with patch("tests.test_utils.TestClient.conversations_create") as patched:
                patched.side_effect = SlackApiError(
                    message="Something didnt go well",
                    response={"error": "This didnt go well"},
                )
                create_channel(book_name="123", client=TestClient())


class TestFormatMessageFromMarkdown:
    def test_empty_message_should_raise(self):
        with pytest.raises(Exception) as exception:
            _markdown_to_slackdown("")
        assert str(exception.value) == "Empty message given "

    @pytest.mark.parametrize(
        "initial_message, expected",
        [
            ("## Heading", "*Heading*"),
            ("This is **bold** text", "This is *bold* text"),
            ("## Title\nSome **bold** format", "*Title*\nSome *bold* format"),
        ],
    )
    def test_markdown_message_should_be_return_as_slack_format(
        self, initial_message, expected
    ):
        assert _markdown_to_slackdown(initial_message) == expected


class TestVerifySlackSignature:
    def setup_method(self, method):
        self.secret = os.getenv("SLACK_SIGNING_SECRET", "test_signature")

    def _generate_signature(self, secret: str, timestamp: str, body: bytes) -> str:
        basestring = f"v0:{timestamp}:{body.decode('utf-8')}"
        return (
            "v0="
            + hmac.new(
                secret.encode(),
                basestring.encode(),
                hashlib.sha256,
            ).hexdigest()
        )

    def test_missing_timestamp_or_signature(self):
        body = b"hello"
        assert verify_slack_request("", "sig", body) is False
        assert verify_slack_request("123", "", body) is False

    def test_timestamp_too_old(self, monkeypatch):
        body = b"hello"
        timestamp = str(int(time.time()) - 4000)
        sig = self._generate_signature(self.secret, timestamp, body)

        assert verify_slack_request(timestamp, sig, body) is False

    def test_invalid_signature(self):
        body = b"hello"
        timestamp = str(int(time.time()))
        bad_sig = "v0=wrong_signature"
        assert verify_slack_request(timestamp, bad_sig, body) is False

    def test_valid_signature(self):
        body = b"hello"
        timestamp = str(int(time.time()))
        sig = self._generate_signature(self.secret, timestamp, body)

        assert verify_slack_request(timestamp, sig, body) is True
