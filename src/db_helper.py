from tinydb import TinyDB, Query
import os
from src.schedule_helper import schedule_jobs
from src.domain import Book
import schedule

db = TinyDB(os.getenv("DB_NAME", "books.json"))
jobs_db = TinyDB(os.getenv("JOBS_DB_NAME", "jobs.json"))


def load_books() -> list[Book]:
    return [Book.from_json(row) for row in db.all()]


def load_book_by_isbn(isbn: str) -> Book | None:
    if not isbn:
        raise Exception("Empty isbn given")

    book = db.search(Query().isbn == isbn)

    if not book:
        return None
    return Book.from_json(book[0])


def write_book_to_db(book: dict) -> None:
    if not book:
        raise Exception("Empty book was given")

    db.upsert(book, Query().isbn == book.get("isbn"))


def load_jobs() -> None:
    jobs = jobs_db.all()
    for element in jobs:
        if element.get("isbn"):
            schedule_jobs(load_book_by_isbn(isbn=element.get("isbn", "")))


def save_jobs() -> None:
    jobs_db.truncate()
    for job in schedule.jobs:
        jobs_db.insert(
            {
                "isbn": job.job_func.args[0].isbn if job.job_func else None,
            }
        )


def reset_jobs() -> None:
    schedule.clear()
    jobs_db.truncate()
