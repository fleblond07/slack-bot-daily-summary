import datetime
from fastapi.testclient import TestClient
from unittest.mock import patch
from datetime import datetime
import os
from tinydb import TinyDB
from src.constant import DEFAULT_SCHEDULE_TIME
import httpx
import schedule
from endpoint import app

from src.main import send_daily_book_summary, send_daily_tech_summary
from tests.test_utils import default_book_for_integration, default_tech_for_integation


client = TestClient(app)


class TestIntegrationTestBookHappyPath:
    def setup_method(self):
        self.jobs_db = TinyDB(os.getenv("JOBS_DB_NAME", "test.json"))
        self.jobs_db.truncate()
        self.db = TinyDB(os.getenv("DB_NAME", "test_db.json"))
        self.db.truncate()
        schedule.clear()

    @patch("src.main.get_channel_id")
    @patch("src.main.get_book_information")
    @patch("endpoint.verify_slack_request")
    @patch("src.main.get_book_isbn")
    @patch("src.ai_helper._send_prompt")
    @patch("src.main.send_slack_message")
    def test_integration_book_happy_path(
        self,
        mock_send_slack,
        mock_gpt,
        mock_isbn,
        mock_verify_slack,
        mock_return_book,
        mock_get_channel,
    ):
        mock_verify_slack.return_value = True
        mock_isbn.return_value = "12345678"
        mock_return_book.return_value = default_book_for_integration
        mock_get_channel.return_value = "1234567"
        mock_gpt.return_value = "This is your daily summary of x"

        response: httpx.Response = client.post(
            "/slack/events",
            data={"command": "/readme", "text": "Johnny McEngineer"},
        )
        assert response.status_code == 200
        assert response.json() == {
            "response_type": "in_channel",
            "text": "Johnny McEngineer will be summarized for you everyday a new chapter at 9am on channel <#1234567>",
        }

        assert len(schedule.jobs) == 1
        job = schedule.jobs[0]
        assert job.job_func.func == send_daily_book_summary
        assert job.job_func.args[0] == default_book_for_integration
        assert (
            getattr(job, "at_time", None)
            == datetime.strptime(DEFAULT_SCHEDULE_TIME, "%H:%M").time()
        )

        job.run()

        mock_send_slack.assert_called_once_with(
            "1234567", "This is your daily summary of x"
        )


class TestIntegrationTestTechHappyPath:
    def setup_method(self):
        self.jobs_db = TinyDB(os.getenv("JOBS_DB_NAME", "test.json"))
        self.jobs_db.truncate()
        self.db = TinyDB(os.getenv("DB_NAME", "test_db.json"))
        self.db.truncate()
        schedule.clear()

    @patch("src.main.get_channel_id")
    @patch("endpoint.verify_slack_request")
    @patch("src.ai_helper._send_prompt")
    @patch("src.main.send_slack_message")
    def test_integration_tech_happy_path(
        self,
        mock_send_slack,
        mock_gpt,
        mock_verify_slack,
        mock_get_channel,
    ):
        mock_verify_slack.return_value = True
        mock_get_channel.return_value = "1234567"
        mock_gpt.return_value = "This is your daily summary of x"

        response: httpx.Response = client.post(
            "/slack/events",
            data={"command": "/tips", "text": "VueJS"},
        )
        assert response.status_code == 200
        assert response.json() == {
            "response_type": "in_channel",
            "text": "We will give you tips and tricks about VueJS everyday on channel <#1234567>",
        }

        assert len(schedule.jobs) == 1
        job = schedule.jobs[0]
        assert job.job_func.func == send_daily_tech_summary
        assert job.job_func.args[0] == default_tech_for_integation
        assert (
            getattr(job, "at_time", None)
            == datetime.strptime(DEFAULT_SCHEDULE_TIME, "%H:%M").time()
        )

        job.run()

        mock_send_slack.assert_called_once_with(
            "1234567", "This is your daily summary of x"
        )
