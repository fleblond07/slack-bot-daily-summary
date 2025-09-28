import schedule
from src.constant import DEFAULT_SCHEDULE_TIME
from src.domain import Book, Technology
import logging


def schedule_jobs(object: Book | Technology | None) -> None:
    from src.main import send_daily_book_summary, send_daily_tech_summary

    logging.info(f"Scheduling job for {type(object)}")

    if not object:
        raise Exception("Called scheduler without a valid object")

    if isinstance(object, Book):
        logging.info(f"Scheduling {object.title}")
        schedule.every().day.at(DEFAULT_SCHEDULE_TIME).do(
            send_daily_book_summary, object
        )
    elif isinstance(object, Technology):
        logging.info(f"Scheduling technology {object.name}")
        schedule.every().day.at(DEFAULT_SCHEDULE_TIME).do(
            send_daily_tech_summary, object
        )
