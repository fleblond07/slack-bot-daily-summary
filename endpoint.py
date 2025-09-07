import asyncio
from contextlib import asynccontextmanager
import schedule
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.db_helper import load_jobs, reset_jobs
from src.main import handle_list_command, handle_readme_command
from src.slack_helper import verify_slack_request
import logging

logger = logging.getLogger("daily_learner")


async def scheduler_loop():
    logger.info("Loading jobs...")
    load_jobs()
    while True:
        logger.info("Checking pending...")
        schedule.run_pending()
        await asyncio.sleep(60)


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

    if not verify_slack_request(timestamp, slack_signature, body):
        logger.warning("Accessing the endpoint without the proper authorization")
        return JSONResponse(status_code=403, content={"error": "Unsupported command"})

    return JSONResponse(content={"response_type": "in_channel", "text": "Hello!"})


@app.post("/slack/reset_schedule")
async def reset_schedule(request: Request) -> JSONResponse:
    timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
    slack_signature = request.headers.get("X-Slack-Signature", "")
    body = await request.body()

    if not verify_slack_request(timestamp, slack_signature, body):
        logger.warning("Accessing the endpoint without the proper authorization")
        return JSONResponse(status_code=403, content={"error": "Unsupported command"})

    reset_jobs()

    return JSONResponse(
        content={"response_type": "in_channel", "text": "Succesful reset!"}
    )


@app.post("/slack/events", response_model=None)
async def slack_events(request: Request) -> JSONResponse | None:
    timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
    slack_signature = request.headers.get("X-Slack-Signature", "")
    body = await request.body()

    if not verify_slack_request(timestamp, slack_signature, body):
        logger.warning("Accessing the endpoint without the proper authorization")
        return JSONResponse(status_code=403, content={"error": "Unsupported command"})

    form = await request.form()
    command = form.get("command")
    text = form.get("text")

    if command not in ["/readme", "/list"]:
        logger.warning("Accessing the endpoint with a unavailable command")
        return JSONResponse(
            content={
                "response_type": "in_channel",
                "text": f"Oh Sorry! the {command=} is not available yet",
            }
        )

    if command == "/readme":
        if not text:
            return JSONResponse(
                content={
                    "response_type": "in_channel",
                    "text": "Oh Sorry! You need to specify the book name you want to search!",
                }
            )
        try:
            result = handle_readme_command(text)
            return JSONResponse(
                content={
                    "response_type": "in_channel",
                    "text": result,
                }
            )
        except Exception as exception:
            return JSONResponse(
                content={
                    "response_type": "in_channel",
                    "text": f"Oh oh! An error occured - {str(exception)}",
                }
            )
    if command == "/list":
        try:
            result = handle_list_command()
            return JSONResponse(
                content={
                    "response_type": "in_channel",
                    "text": result,
                }
            )
        except Exception as exception:
            return JSONResponse(
                content={
                    "response_type": "in_channel",
                    "text": f"Oh oh! An error occured - {str(exception)}",
                }
            )
