import os
import logging
from functools import wraps
from typing import Callable, Awaitable
from fastapi import Request
from fastapi.responses import JSONResponse
from src.slack_helper import verify_slack_request

logger = logging.getLogger("daily_learner")


def require_slack_verification() -> Callable[
    [Callable[[Request], Awaitable[JSONResponse]]],
    Callable[[Request], Awaitable[JSONResponse]],
]:
    """Decorator to verify Slack request signatures before processing requests.

    Returns:
        Decorated function that verifies Slack signatures
    """

    def decorator(
        func: Callable[[Request], Awaitable[JSONResponse]],
    ) -> Callable[[Request], Awaitable[JSONResponse]]:
        @wraps(func)
        async def wrapper(request: Request) -> JSONResponse:
            debug_mode: bool = os.getenv("DEBUG_MODE", "false") == "true"
            timestamp: str = request.headers.get("X-Slack-Request-Timestamp", "")
            slack_signature: str = request.headers.get("X-Slack-Signature", "")
            body: bytes = await request.body()

            if not debug_mode:
                if not verify_slack_request(timestamp, slack_signature, body):
                    logger.warning(
                        "Accessing the endpoint without the proper authorization"
                    )
                    return JSONResponse(
                        status_code=403, content={"error": "Unsupported command"}
                    )
            else:
                logger.warning("⚠️  DEBUG MODE: Security checks bypassed")

            return await func(request)

        return wrapper

    return decorator
