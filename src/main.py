import schedule
from starlette.datastructures import UploadFile
from src.schedule_helper import schedule_jobs
from src.db_helper import (
    load_book_by_isbn,
    load_books,
    load_technology_by_name,
    save_book_jobs,
    save_tech_jobs,
    write_book_to_db,
    write_technology_to_db,
)
from src.ai_helper import (
    get_summary_for_book_by_chapter,
    get_summary_for_book_by_page,
    get_summary_for_technology,
)
from src.domain import Book, ObjectType, State, Technology, Type, Channel
from src.slack_helper import send_slack_message, get_channel_id
from src.external_helper import get_book_information, get_book_isbn
from dotenv import load_dotenv
import os
import logging

load_dotenv()


def send_daily_book_summary(book: Book) -> None:
    print(f"Summarizing book {book.title=}")
    summary: str | None = None
    target_page: int = 0

    if book.type == Type.BY_CHAPTER:
        summary = get_summary_for_book_by_chapter(
            book.title, book.author, book.current_chapter
        )
    if book.type == Type.BY_PAGE:
        target_page = _get_pages_for_summary(book)
        summary = get_summary_for_book_by_page(
            book.title, book.author, target_page, book.current_page
        )

    if not summary:
        raise Exception(f"An error occured getting the summary for book {book.title}")

    send_slack_message(book.channel_id, summary)

    if book.type == Type.BY_CHAPTER:
        book.current_chapter += 1
        if book.chapter_number == book.current_chapter:
            book.state = State.FINISHED
            message = f"This was the final summary for {book.title} - Thank you for using the bot!"
            send_slack_message(book.channel_id, message)
    else:
        book.current_page = target_page
        if (
            book.current_page - 1 == book.page_count
            or book.current_page == book.page_count
            or book.current_page + 1 == book.page_count
        ):
            book.state = State.FINISHED
            message = f"This was the final summary for {book.title} - Thank you for using the bot!"
            send_slack_message(book.channel_id, message)
    write_book_to_db(Book.to_json(book))


def send_daily_tech_summary(technology: Technology) -> None:
    logging.info(f"Tips and tricks for {technology.name=}")

    summary = get_summary_for_technology(technology.name)

    if not summary:
        raise Exception(
            f"An error occured getting tips & tricks for tech {technology.name}"
        )
    logging.info("Sending summary...")
    send_slack_message(technology.channel_id, summary)


def _get_pages_for_summary(book: Book) -> int:
    page_split = book.page_count // int(os.getenv("DEFAULT_PAGES_SPLIT", 15))
    if book.current_page > 0:
        return book.current_page + page_split
    return page_split


def create_book(book_name: str) -> tuple[Book | None, str]:
    isbn: str | None = get_book_isbn(book_name)

    if not isbn:
        raise Exception(f"Cannot find ISBN for {book_name=}")

    book: Book | None = load_book_by_isbn(isbn=isbn)

    if book:
        if book.state == State.FINISHED:
            raise Exception(
                "This book was already completed - Check the channels for the books summary"
            )
        return book, ""

    book_information: Book = get_book_information(isbn)

    book_information.channel_id = get_channel_id(book_information.title)

    write_book_to_db(Book.to_json(book_information))

    return book_information, ""


def handle_readme_command(book_name: UploadFile | str | None) -> str:
    book: Book | None
    err: str | None

    if not isinstance(book_name, str):
        raise Exception(f"Invalid book_name type given {type(book_name)}")

    book, err = create_book(book_name)

    if err:
        return err

    if book:
        schedule_jobs(book)
        save_book_jobs()
        return f"{book.title} will be summarized for you everyday a new chapter at 9am on channel <#{book.channel_id}>"
    return "An error occured while registering the book"


def create_technology(technology_name: str) -> Technology:
    technology: Technology | None = load_technology_by_name(
        technology_name=technology_name
    )

    if technology:
        return technology

    technology = Technology(name=technology_name)

    technology.channel_id = get_channel_id(technology.name)

    write_technology_to_db(Technology.to_json(technology))

    return technology


def handle_tips_command(technology_name: UploadFile | str | None) -> str:
    logging.info("Handling tips command..")
    if not isinstance(technology_name, str):
        raise Exception(f"Invalid technology name type given {type(technology_name)}")

    technology = create_technology(technology_name)

    if technology:
        logging.info(f"Created Technology {technology.name}")
        schedule_jobs(technology)
        logging.info("Saving job information")
        save_tech_jobs()
        return f"We will give you tips and tricks about {technology.name} everyday on channel <#{technology.channel_id}>"
    return "An error occured while registering the technology"


def handle_list_command() -> str:
    channel_list: list = get_all_channel()

    if not channel_list:
        return "An error occured when fetching the channel list"

    channel_links = [
        f"<#{channel.channel_id}>"
        for channel in channel_list
        if hasattr(channel, "channel_id")
    ]
    job_list = []
    for job in schedule.jobs:
        next_run = job.next_run.strftime("%Y-%m-%d %H:%M:%S") if job.next_run else ""
        object_arg = job.job_func.args[0] if job.job_func else ""
        if getattr(object_arg, "object_type", ObjectType.BOOK) == ObjectType.BOOK:
            title = getattr(object_arg, "title", "Unknown")
        else:
            title = getattr(object_arg, "name", "Unknown")
        job_list.append(f"Next run: {next_run}, Title: {title}")
    return (
        "Channels I created:\n"
        + "\n".join(channel_links)
        + "\n"
        + "Current schedule:\n"
        + "\n".join(job_list)
    )


def get_all_channel() -> list[Channel | None]:
    books = load_books()

    return [Channel(channel_id=book.channel_id, book_name=book.title) for book in books]
