import schedule
from constant import DEFAULT_SCHEDULE_TIME
from domain import Book, Technology
import logging
import threading

logger = logging.getLogger("daily_learner")


def schedule_jobs(object: Book | Technology | None) -> None:
    from main import send_daily_book_summary, send_daily_tech_summary

    logger.info(f"Scheduling job for {type(object)}")

    if not object:
        raise Exception("Called scheduler without a valid object")

    if isinstance(object, Book):
        logger.info(f"Scheduling {object.title}")
        schedule.every().day.at(DEFAULT_SCHEDULE_TIME).do(
            send_daily_book_summary, object
        )
    elif isinstance(object, Technology):
        logger.info(f"Scheduling technology {object.name}")
        schedule.every().day.at(DEFAULT_SCHEDULE_TIME).do(
            send_daily_tech_summary, object
        )


def cancel_job_by_isbn(isbn: str) -> None:
    logger.info(f"Attempting to cancel job for {isbn=}")

    for job in schedule.jobs:
        if (
            job.job_func.func.__name__ == "send_daily_book_summary"  # type: ignore[attr-defined]
            and job.job_func.args  # type: ignore[attr-defined]
            and hasattr(job.job_func.args[0], "isbn")  # type: ignore[attr-defined]
            and job.job_func.args[0].isbn == isbn  # type: ignore[attr-defined]
        ):
            logger.info(f"Canceling job for {isbn=}")
            schedule.cancel_job(job)
            return

    logger.info(f"No job found for {isbn=}")


def cancel_job_by_name(name: str) -> None:
    logger.info(f"Attempting to cancel job for {name=}")

    for job in schedule.jobs:
        if (
            job.job_func.func.__name__ == "send_daily_tech_summary"  # type: ignore[attr-defined]
            and job.job_func.args  # type: ignore[attr-defined]
            and hasattr(job.job_func.args[0], "name")  # type: ignore[attr-defined]
            and job.job_func.args[0].name == name  # type: ignore[attr-defined]
        ):
            logger.info(f"Canceling job for {name=}")
            schedule.cancel_job(job)
            return

    logger.info(f"No job found for {name=}")


def run_all_jobs() -> None:
    logger.info("Run all jobs..")

    thread = threading.Thread(name="Run all scheduled jobs", target=schedule.run_all)

    logger.info("Started thread for jobs...")

    thread.start()
