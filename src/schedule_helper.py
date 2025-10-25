import schedule
from src.constant import DEFAULT_SCHEDULE_TIME
from src.domain import Book, Technology, State
import logging
import threading

logger = logging.getLogger("daily_learner")


def _send_book_summary_by_isbn(isbn: str) -> None:
    """Load fresh book data and send summary if book is still ongoing."""
    from src.db_helper import load_book_by_isbn
    from src.main import send_daily_book_summary

    book = load_book_by_isbn(isbn)
    if book and book.state != State.FINISHED:
        send_daily_book_summary(book)


def _send_tech_summary_by_name(name: str) -> None:
    """Load fresh technology data and send summary."""
    from src.db_helper import load_technology_by_name
    from src.main import send_daily_tech_summary

    technology = load_technology_by_name(name)
    if technology:
        send_daily_tech_summary(technology)


def schedule_jobs(object: Book | Technology | None) -> None:
    logger.info(f"Scheduling job for {type(object)}")

    if not object:
        raise Exception("Called scheduler without a valid object")

    if isinstance(object, Book):
        logger.info(f"Scheduling {object.title}")
        schedule.every().day.at(DEFAULT_SCHEDULE_TIME).do(
            _send_book_summary_by_isbn, object.isbn
        )
    elif isinstance(object, Technology):
        logger.info(f"Scheduling technology {object.name}")
        schedule.every().day.at(DEFAULT_SCHEDULE_TIME).do(
            _send_tech_summary_by_name, object.name
        )


def cancel_job_by_isbn(isbn: str) -> None:
    logger.info(f"Attempting to cancel job for {isbn=}")

    for job in schedule.jobs:
        if (
            job.job_func.func.__name__ == "_send_book_summary_by_isbn"  # type: ignore[attr-defined]
            and job.job_func.args  # type: ignore[attr-defined]
            and job.job_func.args[0] == isbn  # type: ignore[attr-defined]
        ):
            logger.info(f"Canceling job for {isbn=}")
            schedule.cancel_job(job)
            return

    logger.info(f"No job found for {isbn=}")


def cancel_job_by_name(name: str) -> None:
    logger.info(f"Attempting to cancel job for {name=}")

    for job in schedule.jobs:
        if (
            job.job_func.func.__name__ == "_send_tech_summary_by_name"  # type: ignore[attr-defined]
            and job.job_func.args  # type: ignore[attr-defined]
            and job.job_func.args[0] == name  # type: ignore[attr-defined]
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
