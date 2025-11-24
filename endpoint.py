import traceback
import asyncio
from contextlib import asynccontextmanager
import schedule
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.secrets_manager import SecretsManager, get_log_level
from src.db_helper import init_db, load_jobs, reset_jobs
from src.main import (
    handle_list_command,
    handle_readme_command,
    handle_tips_command,
    handle_run_command,
)
from src.decorators import require_slack_verification
from src.constant import SCHEDULER_CHECK_INTERVAL_SECONDS
import logging
import logging.config

_secrets_manager = SecretsManager()
LOG_LEVEL = get_log_level()

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
            "level": LOG_LEVEL,
            "handlers": ["console"],
        },
    }
)

logger = logging.getLogger("daily_learner")


async def scheduler_loop():
    logger.info("Initializing database...")
    init_db()
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
@require_slack_verification()
async def slack_hello(request: Request) -> JSONResponse:
    logger.info("Successful Hello, sending back response")
    return JSONResponse(content={"response_type": "in_channel", "text": "Hello!"})


@app.post("/slack/reset_schedule")
@require_slack_verification()
async def reset_schedule(request: Request) -> JSONResponse:
    logger.info("Resetting jobs...")

    reset_jobs()

    logger.info("Job reseted succesfully")

    return JSONResponse(
        content={"response_type": "in_channel", "text": "Successful reset!"}
    )


@app.post("/slack/readme")
@require_slack_verification()
async def slack_readme(request: Request) -> JSONResponse:
    logger.info("Processing readme command")

    form = await request.form()
    text = form.get("text", "")
    command = form.get("command", "")

    if command != "/readme":
        logger.warning(f"Invalid command given {command=}")
        return JSONResponse(status_code=403, content={"error": "Unsupported command"})

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

        result = handle_readme_command(text)

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


@app.post("/slack/list")
@require_slack_verification()
async def slack_list(request: Request) -> JSONResponse:
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


@app.post("/slack/tips")
@require_slack_verification()
async def slack_tips(request: Request) -> JSONResponse:
    try:
        logger.info("Handle tips command")

        form = await request.form()
        text = form.get("text", "")
        command = form.get("command", "")

        if command != "/tips":
            logger.warning(f"Invalid command given {command=}")
            return JSONResponse(
                status_code=403, content={"error": "Unsupported command"}
            )

        result = handle_tips_command(technology_name=text)

        logger.info("Tips command succesful, sending response...")

        return JSONResponse(
            content={
                "response_type": "in_channel",
                "text": result,
            }
        )
    except Exception as exception:
        logger.warning(
            f"An error occurred when processing tips: {traceback.format_exc()}"
        )
        return JSONResponse(
            content={
                "response_type": "in_channel",
                "text": f"Oh oh! An error occurred - {str(exception)}",
            }
        )


@app.post("/slack/run")
@require_slack_verification()
async def slack_run(request: Request) -> JSONResponse:
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
