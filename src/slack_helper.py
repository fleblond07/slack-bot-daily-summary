import re
import time
import traceback
from slack_sdk.web.slack_response import SlackResponse
from typing_extensions import TYPE_CHECKING
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import hmac
import hashlib
import os
from dotenv import load_dotenv

from src.constant import MARKDOWN_RULES
import logging

logger = logging.getLogger("daily_learner")

load_dotenv()

if TYPE_CHECKING:
    from tests.test_utils import TestClient


def send_slack_message(
    channel_id: str, message: str, client: "TestClient | None | WebClient" = None
) -> bool | SlackResponse:
    try:
        if not channel_id or not message:
            raise Exception(f"Wrong argument given {channel_id} - {message}")

        logger.info(f"Sending slack message in {channel_id=}")

        logger.info("Loading web client..")
        client = client or WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

        logger.info("Posting message...")
        response = client.chat_postMessage(
            channel=channel_id, text=_markdown_to_slackdown(message)
        )

        logger.info("Return message status...")
        return response.validate()
    except SlackApiError as e:
        logger.warning(traceback.format_exc())
        raise Exception(f"Error sending message: {e.response['error']}")


def _markdown_to_slackdown(message: str) -> str:
    if not message:
        raise Exception(f"Empty message given {message}")

    logger.info("Processing markdown to slackdown..")

    for pattern, replacement in MARKDOWN_RULES:
        message = re.sub(pattern, replacement, message, flags=re.MULTILINE)

    return message


def get_channel_id(
    object_name: str, client: "TestClient | None | WebClient" = None
) -> str:
    try:
        if not object_name:
            raise Exception("Empty object name given")

        logger.info(f"Get channel_id for {object_name=}")

        client = client or WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

        logger.info("Get the list of channels from Slack...")
        response = client.conversations_list(types="public_channel")

        sanitized_object_name = _sanitize_book_name(object_name)

        for channel in response.get("channels", {}):
            if channel.get("name") == sanitized_object_name:
                logger.info(f"Existing channel found for {object_name=} - Returning ID")
                return channel.get("id", "")

        logger.info(
            f"No existing channel was found for {object_name=} - Creating channel"
        )
        return create_channel(sanitized_object_name)
    except SlackApiError as e:
        raise Exception(f"Error getting channel's id: {e.response['error']}")


def _sanitize_book_name(object_name: str) -> str:
    logger.info(f"Sanitize {object_name=}")
    object_name = object_name.lower().replace(" ", "-")
    return object_name.replace("'", "-")


def create_channel(
    book_name: str, client: "TestClient | WebClient | None" = None
) -> str:
    try:
        if not book_name:
            raise Exception("Empty book name given")

        logger.info(f"Creating channel for {book_name=}")

        client = client or WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

        channel = client.conversations_create(name=book_name)

        logger.info(f"Channel for {book_name=} created succesfully, sending back ID")

        return channel.get("channel", {}).get("id", "")
    except SlackApiError as e:
        raise Exception(f"Error creating channels: {e.response['error']}")


def verify_slack_request(timestamp: str, slack_signature: str, body: bytes) -> bool:
    logger.info("verifying Slack request")

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
