from tinydb import TinyDB, Query
import os
from src.schedule_helper import schedule_jobs
from src.domain import Book, Technology
import schedule
import logging

logger = logging.getLogger("daily_learner")

db = TinyDB(os.getenv("DB_NAME", "books.json"))
jobs_db = TinyDB(os.getenv("JOBS_DB_NAME", "jobs.json"))


def load_books() -> list[Book]:
    logger.info("Loading all books from database")
    return [Book.from_json(row) for row in db.search(Query().object_type == "book")]


def load_technologies() -> list[Technology]:
    logger.info("Loading all technologies from database")
    return [
        Technology.from_json(row) for row in db.search(Query().object_type == "tech")
    ]


def load_book_by_isbn(isbn: str) -> Book | None:
    if not isbn:
        raise Exception("Empty isbn given")

    logger.info(f"Loading book by {isbn=}")

    book = db.search((Query().isbn == isbn) & (Query().object_type == "book"))

    if not book:
        logger.info(f"Book with{isbn=} does not exist in the database")
        return None

    return Book.from_json(book[0])


def write_book_to_db(book: dict) -> None:
    if not book:
        raise Exception("Empty book was given")

    logger.info(f"Writing book {book.get('title', 'Unknown')} to database")

    db.upsert(book, Query().isbn == book.get("isbn"))


def write_technology_to_db(technology: dict) -> None:
    if not technology:
        raise Exception("Invalid technology given")

    logger.info(f"Writing technology {technology.get('name', 'Unknown')}")

    db.upsert(technology, Query().name == technology.get("name"))


def load_technology_by_name(technology_name: str) -> Technology | None:
    if not technology_name:
        raise Exception("Empty technology name given")

    logger.info(f"Loading book by {technology_name=}")

    technology = db.search(
        (Query().name == technology_name) & (Query().object_type == "tech")
    )

    if not technology:
        logger.info(f"{technology_name=} does not exist in the database")
        return None

    return Technology.from_json(technology[0])


def load_jobs() -> None:
    logger.info("Loading jobs from database")
    jobs = jobs_db.all()
    for element in jobs:
        if element.get("object_type") == "book" and element.get("isbn"):
            logger.info("Scheduling book job")
            schedule_jobs(load_book_by_isbn(isbn=element.get("isbn", "")))
        elif element.get("object_type") == "tech":
            logger.info("Scheduling tech job")
            schedule_jobs(
                load_technology_by_name(technology_name=element.get("name", ""))
            )


def save_jobs() -> None:
    logger.info("Saving jobs to database")
    jobs_db.truncate()
    for job in schedule.jobs:
        if isbn := getattr(job.job_func.args[0], "isbn", None):
            logger.info(f"Saving book {isbn=}job to database")
            jobs_db.insert(
                {
                    "isbn": isbn,
                }
            )
        elif name := getattr(job.job_func.args[0], "name", None):
            logger.info(f"Saving technology {name=} job to database")
            jobs_db.insert(
                {
                    "name": name,
                }
            )


def reset_jobs() -> None:
    logger.info("Clearing schedule...")
    schedule.clear()
    logger.info("Clearing jobs DB")
    jobs_db.truncate()
