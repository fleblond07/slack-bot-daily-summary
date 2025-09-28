import re
import time
from slack_sdk.web.slack_response import SlackResponse
from typing_extensions import TYPE_CHECKING
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import hmac
import hashlib
import os
from dotenv import load_dotenv

from src.constant import MARKDOWN_RULES

load_dotenv()

if TYPE_CHECKING:
    from tests.test_utils import TestClient


def send_slack_message(
    channel_id: str, message: str, client: "TestClient | None | WebClient" = None
) -> bool | SlackResponse:
    try:
        if not channel_id or not message:
            raise Exception(f"Wrong argument given {channel_id} - {message}")

        client = client or WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

        response = client.chat_postMessage(
            channel=channel_id, text=_markdown_to_slackdown(message)
        )
        return response.validate()
    except SlackApiError as e:
        raise Exception(f"Error sending message: {e.response['error']}")


def _markdown_to_slackdown(message: str) -> str:
    if not message:
        raise Exception(f"Empty message given {message}")

    for pattern, replacement in MARKDOWN_RULES:
        message = re.sub(pattern, replacement, message, flags=re.MULTILINE)

    return message


def get_channel_id(
    object_name: str, client: "TestClient | None | WebClient" = None
) -> str:
    try:
        if not object_name:
            raise Exception("Empty object name given")

        client = client or WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

        response = client.conversations_list(types="public_channel")
        sanitized_object_name = _sanitize_book_name(object_name)
        for channel in response.get("channels", {}):
            if channel.get("name") == sanitized_object_name:
                return channel.get("id", "")

        return create_channel(sanitized_object_name)
    except SlackApiError as e:
        raise Exception(f"Error getting channel's id: {e.response['error']}")


def _sanitize_book_name(object_name: str) -> str:
    object_name = object_name.lower().replace(" ", "-")
    return object_name.replace("'", "-")


def create_channel(
    book_name: str, client: "TestClient | WebClient | None" = None
) -> str:
    try:
        if not book_name:
            raise Exception("Empty book name given")

        client = client or WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

        channel = client.conversations_create(name=book_name)

        return channel.get("channel", {}).get("id", "")
    except SlackApiError as e:
        raise Exception(f"Error creating channels: {e.response['error']}")


def verify_slack_request(timestamp: str, slack_signature: str, body: bytes) -> bool:
    if not timestamp or not slack_signature:
        return False

    if abs(time.time() - int(timestamp)) > 60 * 5:
        return False

    basestring = f"v0:{timestamp}:{body.decode('utf-8')}"

    expected_signature = (
        "v0="
        + hmac.new(
            os.getenv("SLACK_SIGNING_SECRET", "").encode(),
            basestring.encode(),
            hashlib.sha256,
        ).hexdigest()
    )

    return hmac.compare_digest(expected_signature, slack_signature)
