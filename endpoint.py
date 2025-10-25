import traceback
import asyncio
from contextlib import asynccontextmanager
import schedule
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.db_helper import load_jobs, reset_jobs
from src.main import (
    handle_list_command,
    handle_readme_command,
    handle_tips_command,
    handle_run_command,
)
from src.slack_helper import verify_slack_request
from src.constant import SCHEDULER_CHECK_INTERVAL_SECONDS
import os
import logging
import logging.config
from dotenv import load_dotenv

load_dotenv()

logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
        },
        "root": {
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "handlers": ["console"],
        },
    }
)

logger = logging.getLogger("daily_learner")
debug_mode = os.getenv("DEBUG_MODE", "false") == "true"

if debug_mode:  # pragma: no cover
    logger.warning("=" * 80)
    logger.warning("⚠️  WARNING: DEBUG MODE ENABLED!")
    logger.warning("⚠️  Security checks are bypassed in debug mode.")
    logger.warning("⚠️  DO NOT use debug mode in production environments!")
    logger.warning("=" * 80)


async def scheduler_loop():
    logger.info("Loading jobs...")
    load_jobs()
    while True:
        logger.info("Checking pending...")
        schedule.run_pending()
        await asyncio.sleep(SCHEDULER_CHECK_INTERVAL_SECONDS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(scheduler_loop())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(lifespan=lifespan)


@app.post("/slack/hello")
async def slack_hello(request: Request) -> JSONResponse:
    timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
    slack_signature = request.headers.get("X-Slack-Signature", "")
    body = await request.body()

    if not debug_mode:
        if not verify_slack_request(timestamp, slack_signature, body):
            logger.warning("Accessing the endpoint without the proper authorization")
            return JSONResponse(
                status_code=403, content={"error": "Unsupported command"}
            )
    else:
        logger.warning("⚠️  DEBUG MODE: Security checks bypassed for /slack/hello")

    logger.info("Successful Hello, sending back response")
    return JSONResponse(content={"response_type": "in_channel", "text": "Hello!"})


@app.post("/slack/reset_schedule")
async def reset_schedule(request: Request) -> JSONResponse:
    timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
    slack_signature = request.headers.get("X-Slack-Signature", "")
    body = await request.body()

    if not debug_mode:
        if not verify_slack_request(timestamp, slack_signature, body):
            logger.warning("Accessing the endpoint without the proper authorization")
            return JSONResponse(
                status_code=403, content={"error": "Unsupported command"}
            )
    else:
        logger.warning(
            "⚠️  DEBUG MODE: Security checks bypassed for /slack/reset_schedule"
        )

    logger.info("Resetting jobs...")

    reset_jobs()

    logger.info("Job reseted succesfully")

    return JSONResponse(
        content={"response_type": "in_channel", "text": "Successful reset!"}
    )


@app.post("/slack/events", response_model=None)
async def slack_events(request: Request) -> JSONResponse | None:
    timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
    slack_signature = request.headers.get("X-Slack-Signature", "")
    body = await request.body()

    if not debug_mode:
        if not verify_slack_request(timestamp, slack_signature, body):
            logger.warning("Accessing the endpoint without the proper authorization")
            return JSONResponse(
                status_code=403, content={"error": "Unsupported command"}
            )
    else:
        logger.warning("⚠️  DEBUG MODE: Security checks bypassed for /slack/events")

    logger.info("Processing slack/events..")

    form = await request.form()
    command = form.get("command")
    text = form.get("text")

    logger.info(f"Checking command for {command=} and {text=}")

    if command not in ["/readme", "/list", "/tips", "/run"]:
        logger.warning("Accessing the endpoint with a unavailable command")
        return JSONResponse(
            content={
                "response_type": "in_channel",
                "text": f"Oh Sorry! the {command=} is not available yet",
            }
        )

    if command == "/readme":
        logger.info("Processing readme command")
        if not text:
            logger.warning("Invalid text given for readme command")
            return JSONResponse(
                content={
                    "response_type": "in_channel",
                    "text": "Oh Sorry! You need to specify the book name you want to search!",
                }
            )
        try:
            logger.info("Handling readme command..")

            # Ensure text is a string
            text_str = str(text) if text else None
            result = handle_readme_command(text_str)

            logger.info("Handling readme succesful, sending response..")

            return JSONResponse(
                content={
                    "response_type": "in_channel",
                    "text": result,
                }
            )
        except Exception as exception:
            logger.warning(
                f"An error occurred when processing readme: {traceback.format_exc()}"
            )
            return JSONResponse(
                content={
                    "response_type": "in_channel",
                    "text": f"Oh oh! An error occurred - {str(exception)}",
                }
            )
    if command == "/list":
        try:
            logger.info("Handle list command")

            result = handle_list_command()

            logger.info("List command succesful, sending response...")

            return JSONResponse(
                content={
                    "response_type": "in_channel",
                    "text": result,
                }
            )
        except Exception as exception:
            logger.warning(
                f"An error occurred when processing list: {traceback.format_exc()}"
            )
            return JSONResponse(
                content={
                    "response_type": "in_channel",
                    "text": f"Oh oh! An error occurred - {str(exception)}",
                }
            )
    if command == "/tips":
        try:
            logger.info("Handle tips command")

            # Ensure text is a string
            text_str = str(text) if text else None
            result = handle_tips_command(technology_name=text_str)

            logger.info("Tips command succesful, sending response...")

            return JSONResponse(
                content={
                    "response_type": "in_channel",
                    "text": result,
                }
            )
        except Exception as exception:
            logger.warning(
                f"An error occurred when processing list: {traceback.format_exc()}"
            )
            return JSONResponse(
                content={
                    "response_type": "in_channel",
                    "text": f"Oh oh! An error occurred - {str(exception)}",
                }
            )
    if command == "/run":
        try:
            logger.info("Handle run command")

            result = handle_run_command()

            logger.info("Run command succesful, sending response...")

            return JSONResponse(
                content={
                    "response_type": "in_channel",
                    "text": result,
                }
            )
        except Exception as exception:
            logger.warning(
                f"An error occurred when processing run command: {traceback.format_exc()}"
            )
            return JSONResponse(
                content={
                    "response_type": "in_channel",
                    "text": f"Oh oh! An error occurred - {str(exception)}",
                }
            )
