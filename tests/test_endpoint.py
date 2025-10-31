from fastapi.testclient import TestClient
from unittest.mock import patch
from endpoint import app
import time


client = TestClient(app)


class TestSlackHello:
    def test_slack_hello_valid_signature(self):
        with patch("src.decorators.verify_slack_request", return_value=True):
            response = client.post("/slack/hello", content=b"{}")
        assert response.status_code == 200
        assert response.json() == {
            "response_type": "in_channel",
            "text": "Hello!",
        }

    def test_slack_hello_invalid_signature(self):
        with patch("src.decorators.verify_slack_request", return_value=False):
            response = client.post("/slack/hello", content=b"{}")
        assert response.status_code == 403
        assert response.json()["error"] == "Unsupported command"


class TestSlackResetSchedule:
    def test_reset_schedule_valid_signature(self):
        with (
            patch("src.decorators.verify_slack_request", return_value=True),
            patch("endpoint.reset_jobs") as mock_reset,
        ):
            response = client.post("/slack/reset_schedule", content=b"{}")
        mock_reset.assert_called_once()
        assert response.status_code == 200
        assert "Successful reset!" in response.json()["text"]

    def test_reset_schedule_invalid_signature(self):
        with patch("src.decorators.verify_slack_request", return_value=False):
            response = client.post("/slack/reset_schedule", content=b"{}")
        assert response.status_code == 403
        assert response.json()["error"] == "Unsupported command"


class TestSlackReadme:
    def test_readme_no_text(self):
        with patch("src.decorators.verify_slack_request", return_value=True):
            response = client.post(
                "/slack/readme",
                data={"text": "", "command": "/readme"},
            )
        assert "need to specify the book" in response.json()["text"]

    def test_readme_success(self):
        with (
            patch("src.decorators.verify_slack_request", return_value=True),
            patch("endpoint.handle_readme_command", return_value="Book found!"),
        ):
            response = client.post(
                "/slack/readme",
                data={"text": "Python", "command": "/readme"},
            )
        assert response.json()["text"] == "Book found!"

    def test_readme_failure(self):
        with (
            patch("src.decorators.verify_slack_request", return_value=True),
            patch(
                "endpoint.handle_readme_command",
                side_effect=Exception("Error occurred"),
            ),
        ):
            response = client.post(
                "/slack/readme",
                data={"text": "Python", "command": "/readme"},
            )
        assert response.json()["text"] == "Oh oh! An error occurred - Error occurred"

    def test_readme_invalid_command(self):
        with patch("src.decorators.verify_slack_request", return_value=True):
            response = client.post(
                "/slack/readme",
                data={"text": "Python", "command": "/wrongcommand"},
            )
        assert response.status_code == 403
        assert response.json()["error"] == "Unsupported command"

    def test_readme_invalid_signature(self):
        with patch("src.decorators.verify_slack_request", return_value=False):
            response = client.post(
                "/slack/readme",
                data={"text": "Python", "command": "/readme"},
            )
        assert response.status_code == 403


class TestSlackList:
    def test_list_success(self):
        with (
            patch("src.decorators.verify_slack_request", return_value=True),
            patch(
                "endpoint.handle_list_command",
                return_value="Below the list of channels",
            ),
        ):
            response = client.post(
                "/slack/list",
                data={},
            )
        assert response.json()["text"] == "Below the list of channels"

    def test_list_exception(self):
        with (
            patch("src.decorators.verify_slack_request", return_value=True),
            patch("endpoint.handle_list_command", side_effect=Exception("Oops")),
        ):
            response = client.post(
                "/slack/list",
                data={},
            )
        assert "An error occurred" in response.json()["text"]

    def test_list_invalid_signature(self):
        with patch("src.decorators.verify_slack_request", return_value=False):
            response = client.post(
                "/slack/list",
                data={},
            )
        assert response.status_code == 403


class TestSlackTips:
    def test_tips_success(self):
        with (
            patch("src.decorators.verify_slack_request", return_value=True),
            patch("endpoint.handle_tips_command", return_value="Here are some tips!"),
        ):
            response = client.post(
                "/slack/tips",
                data={"text": "Python", "command": "/tips"},
            )
        assert response.json()["text"] == "Here are some tips!"
        assert response.json()["response_type"] == "in_channel"

    def test_tips_exception(self):
        with (
            patch("src.decorators.verify_slack_request", return_value=True),
            patch("endpoint.handle_tips_command", side_effect=Exception("Oops")),
        ):
            response = client.post(
                "/slack/tips",
                data={"text": "Python", "command": "/tips"},
            )
        assert "Oh oh! An error occurred - Oops" in response.json()["text"]
        assert response.json()["response_type"] == "in_channel"

    def test_tips_invalid_command(self):
        with patch("src.decorators.verify_slack_request", return_value=True):
            response = client.post(
                "/slack/tips",
                data={"text": "Python", "command": "/wrongcommand"},
            )
        assert response.status_code == 403
        assert response.json()["error"] == "Unsupported command"

    def test_tips_invalid_signature(self):
        with patch("src.decorators.verify_slack_request", return_value=False):
            response = client.post(
                "/slack/tips",
                data={"text": "Python", "command": "/tips"},
            )
        assert response.status_code == 403


class TestSlackRun:
    def test_run_success(self):
        with (
            patch("src.decorators.verify_slack_request", return_value=True),
            patch(
                "endpoint.handle_run_command",
                return_value="Jobs executed successfully!",
            ),
        ):
            response = client.post(
                "/slack/run",
                data={},
            )
        assert response.status_code == 200
        json_data: dict[str, str] = response.json()
        assert json_data["response_type"] == "in_channel"
        assert json_data["text"] == "Jobs executed successfully!"

    def test_run_failure(self):
        with (
            patch("src.decorators.verify_slack_request", return_value=True),
            patch(
                "endpoint.handle_run_command",
                side_effect=Exception("Something went wrong"),
            ),
        ):
            response = client.post(
                "/slack/run",
                data={},
            )
        assert response.status_code == 200
        json_data: dict[str, str] = response.json()
        assert json_data["response_type"] == "in_channel"
        assert json_data["text"] == "Oh oh! An error occurred - Something went wrong"

    def test_run_invalid_signature(self):
        with patch("src.decorators.verify_slack_request", return_value=False):
            response = client.post(
                "/slack/run",
                data={},
            )
        assert response.status_code == 403


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


class TestDebugMode:
    def test_slack_hello_bypasses_security_in_debug_mode(self):
        with patch("src.decorators.os.getenv", return_value="true"):
            response = client.post("/slack/hello", content=b"{}")
        assert response.status_code == 200
        assert response.json() == {
            "response_type": "in_channel",
            "text": "Hello!",
        }

    def test_slack_reset_bypasses_security_in_debug_mode(self):
        with (
            patch("src.decorators.os.getenv", return_value="true"),
            patch("endpoint.reset_jobs") as mock_reset,
        ):
            response = client.post("/slack/reset_schedule", content=b"{}")
        mock_reset.assert_called_once()
        assert response.status_code == 200

    def test_slack_list_bypasses_security_in_debug_mode(self):
        with (
            patch("src.decorators.os.getenv", return_value="true"),
            patch("endpoint.handle_list_command", return_value="List of channels"),
        ):
            response = client.post(
                "/slack/list",
                data={},
            )
        assert response.status_code == 200
        assert response.json()["text"] == "List of channels"

    def test_slack_readme_bypasses_security_in_debug_mode(self):
        with (
            patch("src.decorators.os.getenv", return_value="true"),
            patch("endpoint.handle_readme_command", return_value="Book content"),
        ):
            response = client.post(
                "/slack/readme",
                data={"text": "Python", "command": "/readme"},
            )
        assert response.status_code == 200
        assert response.json()["text"] == "Book content"

    def test_slack_tips_bypasses_security_in_debug_mode(self):
        with (
            patch("src.decorators.os.getenv", return_value="true"),
            patch("endpoint.handle_tips_command", return_value="Tips content"),
        ):
            response = client.post(
                "/slack/tips",
                data={"text": "React", "command": "/tips"},
            )
        assert response.status_code == 200
        assert response.json()["text"] == "Tips content"

    def test_slack_run_bypasses_security_in_debug_mode(self):
        with (
            patch("src.decorators.os.getenv", return_value="true"),
            patch("endpoint.handle_run_command", return_value="Jobs executed"),
        ):
            response = client.post(
                "/slack/run",
                data={},
            )
        assert response.status_code == 200
        assert response.json()["text"] == "Jobs executed"
