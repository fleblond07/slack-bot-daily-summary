from tinydb import TinyDB, Query
import os
from src.schedule_helper import schedule_jobs
from src.domain import Book, Technology
import schedule

db = TinyDB(os.getenv("DB_NAME", "books.json"))
jobs_db = TinyDB(os.getenv("JOBS_DB_NAME", "jobs.json"))


def load_books() -> list[Book]:
    return [Book.from_json(row) for row in db.search(Query().object_type == "book")]


def load_book_by_isbn(isbn: str) -> Book | None:
    if not isbn:
        raise Exception("Empty isbn given")

    book = db.search((Query().isbn == isbn) & (Query().object_type == "book"))

    if not book:
        return None
    return Book.from_json(book[0])


def write_book_to_db(book: dict) -> None:
    if not book:
        raise Exception("Empty book was given")

    db.upsert(book, Query().isbn == book.get("isbn"))


def write_technology_to_db(technology: dict) -> None:
    if not technology:
        raise Exception("Invalid technology given")

    db.upsert(technology, Query().name == technology.get("name"))


def load_technology_by_name(technology_name: str) -> Technology | None:
    if not technology_name:
        raise Exception("Empty technology name given")

    technology = db.search(
        (Query().name == technology_name) & (Query().object_type == "tech")
    )
    if not technology:
        return None

    return Technology.from_json(technology[0])


def load_jobs() -> None:
    jobs = jobs_db.all()
    for element in jobs:
        if element.get("object_type") == "book" and element.get("isbn"):
            schedule_jobs(load_book_by_isbn(isbn=element.get("isbn", "")))
        elif element.get("object_type") == "tech":
            schedule_jobs(
                load_technology_by_name(technology_name=element.get("name", ""))
            )


def save_book_jobs() -> None:
    jobs_db.truncate()
    for job in schedule.jobs:
        jobs_db.insert(
            {
                "isbn": job.job_func.args[0].isbn if job.job_func else None,
            }
        )


def save_tech_jobs() -> None:
    jobs_db.truncate()
    for job in schedule.jobs:
        jobs_db.insert(
            {
                "name": job.job_func.args[0].name if job.job_func else None,
            }
        )


def reset_jobs() -> None:
    schedule.clear()
    jobs_db.truncate()
