from fastapi.testclient import TestClient
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from unittest.mock import patch
from decorators import require_slack_verification

app = FastAPI()


@app.post("/test_valid")
@require_slack_verification()
async def endpoint_valid(request: Request) -> JSONResponse:
    return JSONResponse(content={"message": "success"})


@app.post("/test_invalid")
@require_slack_verification()
async def endpoint_invalid(request: Request) -> JSONResponse:
    return JSONResponse(content={"message": "success"})


client = TestClient(app)


class TestRequireSlackVerification:
    """Test the require_slack_verification decorator."""

    def test_decorator_allows_valid_signature(self):
        """Test that decorator allows request with valid signature."""
        with patch("decorators.verify_slack_request", return_value=True):
            response = client.post("/test_valid", content=b'{"test": "data"}')

        assert response.status_code == 200
        assert response.json() == {"message": "success"}

    def test_decorator_blocks_invalid_signature(self):
        """Test that decorator blocks request with invalid signature."""
        with (
            patch("decorators.get_debug_mode", return_value=False),
            patch("decorators.verify_slack_request", return_value=False),
        ):
            response = client.post("/test_invalid", content=b'{"test": "data"}')

        assert response.status_code == 403
        assert response.json() == {"error": "Unsupported command"}

    def test_decorator_bypasses_security_in_debug_mode(self):
        """Test that decorator bypasses verification in debug mode."""
        with patch("decorators.get_debug_mode", return_value=True):
            response = client.post("/test_valid", content=b'{"test": "data"}')

        assert response.status_code == 200
        assert response.json() == {"message": "success"}

    def test_decorator_handles_missing_headers(self):
        """Test that decorator handles missing Slack headers."""
        with (
            patch("decorators.get_debug_mode", return_value=False),
            patch("decorators.verify_slack_request", return_value=False),
        ):
            response = client.post("/test_valid", content=b'{"test": "data"}')

        assert response.status_code == 403
        assert response.json() == {"error": "Unsupported command"}
