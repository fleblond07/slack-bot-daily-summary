import schedule
from src.constant import DEFAULT_SCHEDULE_TIME
from src.domain import Book


def schedule_jobs(book: Book | None) -> None:
    from src.main import send_daily_summary

    if not book:
        raise Exception("Called scheduler without a book")

    schedule.every().day.at(DEFAULT_SCHEDULE_TIME).do(send_daily_summary, book)
