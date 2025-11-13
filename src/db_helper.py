import sqlite3
from contextlib import contextmanager
from src.schedule_helper import schedule_jobs
from src.domain import Book, ObjectType, Technology
from src.constant import DB_NAME, JOBS_DB_NAME
import schedule
import logging

logger = logging.getLogger("daily_learner")


@contextmanager
def get_db_connection(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_main_db():
    with get_db_connection(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                object_type TEXT NOT NULL,
                object_id INTEGER NOT NULL,
                UNIQUE(object_type, object_id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                isbn TEXT UNIQUE NOT NULL,
                title TEXT,
                author TEXT,
                page_count INTEGER,
                state TEXT,
                type TEXT,
                chapter_number INTEGER,
                current_chapter INTEGER,
                current_page INTEGER,
                email TEXT DEFAULT '',
                notification_channel TEXT DEFAULT 'slack'
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS technologies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                email TEXT DEFAULT '',
                notification_channel TEXT DEFAULT 'slack'
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS channels (
                channel_id TEXT NOT NULL,
                object_id INTEGER UNIQUE NOT NULL
            )
        """)


def init_jobs_db():
    with get_db_connection(JOBS_DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                isbn TEXT,
                name TEXT
            )
        """)


init_main_db()
init_jobs_db()


def load_books() -> list[Book]:
    logger.info("Loading all books from database")
    with get_db_connection(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT b.*, c.channel_id
            FROM books b
            LEFT JOIN channels c ON c.object_id = b.id
        """
        )
        rows = cursor.fetchall()
        books = []
        for row in rows:
            book_dict = dict(row)
            book_dict["object_type"] = ObjectType.BOOK.value
            books.append(Book.from_json(book_dict))
        return books


def load_technologies() -> list[Technology]:
    logger.info("Loading all technologies from database")
    with get_db_connection(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT t.*, c.channel_id
            FROM technologies t
            LEFT JOIN channels c ON c.object_id = t.id
        """
        )
        rows = cursor.fetchall()
        techs = []
        for row in rows:
            tech_dict = dict(row)
            tech_dict["object_type"] = ObjectType.TECH.value
            techs.append(Technology.from_json(tech_dict))
        return techs


def load_book_by_isbn(isbn: str) -> Book | None:
    if not isbn:
        raise Exception("Empty isbn given")

    logger.info(f"Loading book by {isbn=}")

    with get_db_connection(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT b.*, c.channel_id
            FROM books b
            LEFT JOIN channels c ON c.object_id = b.id
            WHERE b.isbn = ?
        """,
            (isbn,),
        )
        row = cursor.fetchone()

        if not row:
            logger.info(f"Book with{isbn=} does not exist in the database")
            return None

        book_dict = dict(row)
        book_dict["object_type"] = ObjectType.BOOK.value
        return Book.from_json(book_dict)


def write_book_to_db(book: dict) -> None:
    if not book:
        raise Exception("Empty book was given")

    logger.info(f"Writing book {book.get('title', 'Unknown')} to database")

    with get_db_connection(DB_NAME) as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO books (
                isbn, title, author, page_count, state, type,
                chapter_number, current_chapter, current_page,
                email, notification_channel
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(isbn) DO UPDATE SET
                title = excluded.title,
                author = excluded.author,
                page_count = excluded.page_count,
                state = excluded.state,
                type = excluded.type,
                chapter_number = excluded.chapter_number,
                current_chapter = excluded.current_chapter,
                current_page = excluded.current_page,
                email = excluded.email,
                notification_channel = excluded.notification_channel
            """,
            (
                book.get("isbn"),
                book.get("title"),
                book.get("author"),
                book.get("page_count"),
                book.get("state"),
                book.get("type"),
                book.get("chapter_number"),
                book.get("current_chapter"),
                book.get("current_page"),
                book.get("email", ""),
                book.get("notification_channel", "slack"),
            ),
        )

        cursor.execute("SELECT id FROM books WHERE isbn = ?", (book.get("isbn"),))
        book_id = cursor.fetchone()[0]
        cursor.execute(
            """
            INSERT INTO items (object_type, object_id)
            VALUES (?, ?)
            ON CONFLICT(object_type, object_id) DO NOTHING
            """,
            (ObjectType.BOOK.value, book_id),
        )

        if channel_id := book.get("channel_id"):
            cursor.execute(
                """
                INSERT INTO channels (channel_id, object_id)
                VALUES (?, ?)
                ON CONFLICT(object_id) DO UPDATE SET
                    channel_id = excluded.channel_id
                """,
                (channel_id, book_id),
            )


def write_technology_to_db(technology: dict) -> None:
    if not technology:
        raise Exception("Invalid technology given")

    logger.info(f"Writing technology {technology.get('name', 'Unknown')}")

    with get_db_connection(DB_NAME) as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO technologies (name, email, notification_channel)
            VALUES (?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                email = excluded.email,
                notification_channel = excluded.notification_channel
            """,
            (
                technology.get("name"),
                technology.get("email", ""),
                technology.get("notification_channel", "slack"),
            ),
        )

        cursor.execute(
            "SELECT id FROM technologies WHERE name = ?", (technology.get("name"),)
        )
        tech_id = cursor.fetchone()[0]
        cursor.execute(
            """
            INSERT INTO items (object_type, object_id)
            VALUES (?, ?)
            ON CONFLICT(object_type, object_id) DO NOTHING
            """,
            (ObjectType.TECH.value, tech_id),
        )

        if channel_id := technology.get("channel_id"):
            cursor.execute(
                """
                INSERT INTO channels (channel_id, object_id)
                VALUES (?, ?)
                ON CONFLICT(object_id) DO UPDATE SET
                    channel_id = excluded.channel_id
                """,
                (channel_id, tech_id),
            )


def load_technology_by_name(technology_name: str) -> Technology | None:
    if not technology_name:
        raise Exception("Empty technology name given")

    logger.info(f"Loading technology by {technology_name=}")

    with get_db_connection(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT t.*, c.channel_id
            FROM technologies t
            LEFT JOIN channels c ON c.object_id = t.id
            WHERE t.name = ?
        """,
            (technology_name,),
        )
        row = cursor.fetchone()

        if not row:
            logger.info(f"{technology_name=} does not exist in the database")
            return None

        tech_dict = dict(row)
        tech_dict["object_type"] = ObjectType.TECH.value
        return Technology.from_json(tech_dict)


def load_jobs() -> None:
    logger.info("Loading jobs from database")
    with get_db_connection(JOBS_DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jobs")
        jobs = cursor.fetchall()

        for element in jobs:
            element_dict = dict(element)
            if isbn := element_dict.get("isbn", None):
                logger.info("Scheduling book job")
                schedule_jobs(load_book_by_isbn(isbn=isbn))
            elif name := element_dict.get("name", None):
                logger.info("Scheduling tech job")
                schedule_jobs(load_technology_by_name(technology_name=name))


def save_jobs() -> None:
    logger.info("Saving jobs to database")
    with get_db_connection(JOBS_DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM jobs")

        for job in schedule.jobs:
            if isbn := getattr(job.job_func.args[0], "isbn", None):  # type: ignore[attr-defined]
                logger.info(f"Saving book {isbn=} job to database")
                cursor.execute("INSERT INTO jobs (isbn) VALUES (?)", (isbn,))
            elif name := getattr(job.job_func.args[0], "name", None):  # type: ignore[attr-defined]
                logger.info(f"Saving technology {name=} job to database")
                cursor.execute("INSERT INTO jobs (name) VALUES (?)", (name,))


def reset_jobs() -> None:
    logger.info("Clearing schedule...")
    schedule.clear()
    logger.info("Clearing jobs DB")
    with get_db_connection(JOBS_DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM jobs")
