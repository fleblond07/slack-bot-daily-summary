from fastapi.testclient import TestClient
from unittest.mock import patch

import httpx
from endpoint import app
import time

from tests.test_utils import default_book_per_page_from_google


client = TestClient(app)


class TestIntegrationTestBookHappyPath:
    @patch("src.main.get_channel_id")
    @patch("src.main.get_book_information")
    @patch("endpoint.verify_slack_request")
    @patch("src.main.get_book_isbn")
    def test_integration_book_happy_path(
        self, mock_isbn, mock_verify_slack, mock_return_book, mock_get_channel
    ):
        mock_verify_slack.return_value = True
        mock_isbn.return_value = "12345678"
        mock_return_book.return_value = default_book_per_page_from_google
        mock_get_channel.channel_id = "1234567"

        response: httpx.Response = client.post(
            "/slack/events",
            data={"command": "/readme", "text": "Johnny McEngineer"},
        )
        assert response.status_code == 200
        toto = response.json()
        breakpoint()
        assert response.json() == {
            "response_type": "in_channel",
            "text": "Hello!",
        }
