from fastapi.testclient import TestClient
from unittest.mock import patch
from endpoint import app
import time


client = TestClient(app)


class TestSlackHello:
    def test_slack_hello_valid_signature(self):
        with patch("endpoint.verify_slack_request", return_value=True):
            response = client.post("/slack/hello", content=b"{}")
        assert response.status_code == 200
        assert response.json() == {
            "response_type": "in_channel",
            "text": "Hello!",
        }

    def test_slack_hello_invalid_signature(self):
        with patch("endpoint.verify_slack_request", return_value=False):
            response = client.post("/slack/hello", content=b"{}")
        assert response.status_code == 403
        assert response.json()["error"] == "Unsupported command"


class TestSlackResetSchedule:
    def test_reset_schedule_valid_signature(self):
        with (
            patch("endpoint.verify_slack_request", return_value=True),
            patch("endpoint.reset_jobs") as mock_reset,
        ):
            response = client.post("/slack/reset_schedule", content=b"{}")
        mock_reset.assert_called_once()
        assert response.status_code == 200
        assert "Succesful reset!" in response.json()["text"]

    def test_reset_schedule_invalid_signature(self):
        with patch("endpoint.verify_slack_request", return_value=False):
            response = client.post("/slack/reset_schedule", content=b"{}")
        assert response.status_code == 403
        assert response.json()["error"] == "Unsupported command"


class TestSlackEvents:
    def test_unavailable_command(self):
        with patch("endpoint.verify_slack_request", return_value=True):
            response = client.post(
                "/slack/events",
                data={"command": "/unknown", "text": "test"},
            )
        assert "not available yet" in response.json()["text"]

    def test_readme_no_text(self):
        with patch("endpoint.verify_slack_request", return_value=True):
            response = client.post(
                "/slack/events",
                data={"command": "/readme"},
            )
        assert "need to specify the book" in response.json()["text"]

    def test_readme_success(self):
        with (
            patch("endpoint.verify_slack_request", return_value=True),
            patch("endpoint.handle_readme_command", return_value="Book found!"),
        ):
            response = client.post(
                "/slack/events",
                data={"command": "/readme", "text": "Python"},
            )
        assert response.json()["text"] == "Book found!"

    def test_readme_failure(self):
        with (
            patch("endpoint.verify_slack_request", return_value=True),
            patch(
                "endpoint.handle_readme_command", side_effect=Exception("Error occured")
            ),
        ):
            response = client.post(
                "/slack/events",
                data={"command": "/readme", "text": "Python"},
            )
        assert response.json()["text"] == "Oh oh! An error occured - Error occured"

    def test_list_success(self):
        with (
            patch("endpoint.verify_slack_request", return_value=True),
            patch(
                "endpoint.handle_list_command",
                return_value="Below the list of channels",
            ),
        ):
            response = client.post(
                "/slack/events",
                data={"command": "/list", "text": ""},
            )
        assert response.json()["text"] == "Below the list of channels"

    def test_list_exception(self):
        with (
            patch("endpoint.verify_slack_request", return_value=True),
            patch("endpoint.handle_list_command", side_effect=Exception("Oops")),
        ):
            response = client.post(
                "/slack/events",
                data={"command": "/list"},
            )
        assert "An error occured" in response.json()["text"]

    def test_invalid_signature(self):
        with patch("endpoint.verify_slack_request", return_value=False):
            response = client.post(
                "/slack/events",
                data={"command": "/list"},
            )
        assert response.status_code == 403

    def test_tips_success(self):
        with (
            patch("endpoint.verify_slack_request", return_value=True),
            patch("endpoint.handle_tips_command", return_value="Here are some tips!"),
        ):
            response = client.post(
                "/slack/events",
                data={"command": "/tips", "text": "Python"},
            )
        assert response.json()["text"] == "Here are some tips!"
        assert response.json()["response_type"] == "in_channel"

    def test_tips_exception(self):
        with (
            patch("endpoint.verify_slack_request", return_value=True),
            patch("endpoint.handle_tips_command", side_effect=Exception("Oops")),
        ):
            response = client.post(
                "/slack/events",
                data={"command": "/tips", "text": "Python"},
            )
        assert "Oh oh! An error occured - Oops" in response.json()["text"]
        assert response.json()["response_type"] == "in_channel"

    def test_run_success(self):
        with (
            patch("endpoint.verify_slack_request", return_value=True),
            patch(
                "endpoint.handle_run_command",
                return_value="Jobs executed successfully!",
            ),
        ):
            response = client.post(
                "/slack/events",
                data={"command": "/run"},
            )
        assert response.status_code == 200
        json_data: dict[str, str] = response.json()
        assert json_data["response_type"] == "in_channel"
        assert json_data["text"] == "Jobs executed successfully!"

    def test_run_failure(self):
        with (
            patch("endpoint.verify_slack_request", return_value=True),
            patch(
                "endpoint.handle_run_command",
                side_effect=Exception("Something went wrong"),
            ),
        ):
            response = client.post(
                "/slack/events",
                data={"command": "/run"},
            )
        assert response.status_code == 200
        json_data: dict[str, str] = response.json()
        assert json_data["response_type"] == "in_channel"
        assert json_data["text"] == "Oh oh! An error occured - Something went wrong"


class TestSchedulerLifespan:
    def test_scheduler_loop_started_and_cancelled_on_shutdown(self):
        with (
            patch("endpoint.load_jobs") as mock_load_jobs,
            patch("endpoint.schedule.run_pending") as mock_run_pending,
        ):
            with TestClient(app):
                time.sleep(0.2)
        mock_load_jobs.assert_called_once()
        assert mock_run_pending.called
