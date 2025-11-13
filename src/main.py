import logging

import schedule
from starlette.datastructures import UploadFile

from src.ai_helper import (
    get_summary_for_book_by_chapter,
    get_summary_for_book_by_page,
    get_summary_for_technology,
)
from src.constant import DEFAULT_PAGES_SPLIT
from src.db_helper import (
    load_book_by_isbn,
    load_books,
    load_technologies,
    load_technology_by_name,
    save_jobs,
    write_book_to_db,
    write_technology_to_db,
)
from src.domain import Book, Channel, ObjectType, State, Technology, Type
from src.external_helper import get_book_information, get_book_isbn
from src.notification_helper import NotificationChannel, send_notification
from src.schedule_helper import cancel_job_by_isbn, run_all_jobs, schedule_jobs
from src.slack_helper import get_channel_id

logger = logging.getLogger("daily_learner")


def send_daily_book_summary(book: Book) -> None:
    logger.info(f"Summarizing book {book.title=}")
    summary: str | None = None
    target_page: int = 0

    if book.type == Type.BY_CHAPTER:
        logger.info("Getting summary for book by chapter")
        summary = get_summary_for_book_by_chapter(
            book.title, book.author, book.current_chapter
        )
    elif book.type == Type.BY_PAGE:
        logger.info("Getting summary for book by page")
        target_page = _get_pages_for_summary(book)
        summary = get_summary_for_book_by_page(
            book.title, book.author, target_page, book.current_page
        )
    else:
        raise ValueError(f"Unknown book type: {book.type}")

    if not summary:
        raise Exception(f"An error occurred getting the summary for book {book.title}")

    logger.info(
        f"Sending notification that contains summary... via {book.notification_channel}"
    )

    notification_channel = NotificationChannel(book.notification_channel)

    send_notification(
        channel_id=book.channel_id,
        email=book.email,
        subject=f"Daily Summary: {book.title}",
        message=summary,
        notification_channel=notification_channel,
    )

    if book.type == Type.BY_CHAPTER:
        logger.info("Update current chapter number and status")
        book.current_chapter += 1
        if book.chapter_number == book.current_chapter:
            logger.info(f"Final chapter for {book.title} - Changing status to finished")
            book.state = State.FINISHED
            message = f"This was the final summary for {book.title} - Thank you for using the bot!"
            logger.info(
                f"Sending last message for {book.title} via {book.notification_channel}"
            )
            send_notification(
                channel_id=book.channel_id,
                email=book.email,
                subject=f"Final Summary: {book.title}",
                message=message,
                notification_channel=notification_channel,
            )

            cancel_job_by_isbn(book.isbn)
    else:
        logger.info("Update current page number and status")
        book.current_page = target_page
        if book.current_page >= book.page_count:
            logger.info(
                f"Final page range for {book.title} - Changing status to finished"
            )
            book.state = State.FINISHED
            message = f"This was the final summary for {book.title} - Thank you for using the bot!"
            logger.info(
                f"Sending last message for {book.title} via {book.notification_channel}"
            )
            send_notification(
                channel_id=book.channel_id,
                email=book.email,
                subject=f"Final Summary: {book.title}",
                message=message,
                notification_channel=notification_channel,
            )

            cancel_job_by_isbn(book.isbn)

    logger.info("Writing updated book to database")

    write_book_to_db(Book.to_json(book))


def send_daily_tech_summary(technology: Technology) -> None:
    logger.info(f"Tips and tricks for {technology.name=}")

    summary = get_summary_for_technology(technology.name)

    if not summary:
        raise Exception(
            f"An error occurred getting tips & tricks for tech {technology.name}"
        )

    logger.info(
        f"Sending tips for {technology.name} via {technology.notification_channel}"
    )

    notification_channel = NotificationChannel(technology.notification_channel)

    send_notification(
        channel_id=technology.channel_id,
        email=technology.email,
        subject=f"Daily Tips: {technology.name}",
        message=summary,
        notification_channel=notification_channel,
    )


def _get_pages_for_summary(book: Book) -> int:
    logger.info("Getting page numbers for summary")
    page_split = book.page_count // DEFAULT_PAGES_SPLIT
    if book.current_page > 0:
        return book.current_page + page_split
    return page_split


def create_book(book_name: str) -> tuple[Book | None, str]:
    logger.info("Creating book..")
    isbn: str | None = get_book_isbn(book_name)

    if not isbn:
        raise Exception(f"Cannot find ISBN for {book_name=}")

    logger.info(f"Searching for book {book_name=}")
    book: Book | None = load_book_by_isbn(isbn=isbn)

    if book:
        logger.info(f"Book {book_name=} already in database, returning db object")
        if book.state == State.FINISHED:
            raise Exception(
                "This book was already completed - Check the channels for the books summary"
            )
        return book, ""

    logger.info(f"{book_name=} not found in database, creating object..")

    book_information: Book = get_book_information(isbn)

    logger.info(f"Get channel ID for {book_name=}")

    book_information.channel_id = get_channel_id(book_information.title)

    logger.info(f"Write {book_name=} to DB")

    write_book_to_db(Book.to_json(book_information))

    return book_information, ""


def handle_run_command() -> str:
    logger.info("Handling run command")

    run_all_jobs()

    logger.info("Running all jobs..")

    return "I have succesfully started all scheduled jobs"


def handle_readme_command(book_name: str | UploadFile | None) -> str:
    logger.info("Handling readme command")
    book: Book | None
    err: str | None

    if not book_name or not isinstance(book_name, str):
        raise Exception("book_name is required")

    logger.info("Creating book")

    book, err = create_book(book_name)

    if err:
        logger.warning(f"An error occurred when creating the book: {err=}")
        return err

    if book:
        logger.info(f"Registering {book_name=} on schedule and jobs DB")
        schedule_jobs(book)
        save_jobs()
        return f"{book.title} will be summarized for you everyday a new chapter at 9am on channel <#{book.channel_id}>"
    return "An error occurred while registering the book"


def create_technology(technology_name: str) -> Technology:
    logger.info("Search for existing technology..")

    technology: Technology | None = load_technology_by_name(
        technology_name=technology_name
    )

    if technology:
        logger.info(f"{technology_name=} already exist in db, returning db object")
        return technology

    logger.info(f"{technology_name=} does not exist yet, creating object..")

    technology = Technology(name=technology_name)

    logger.info(f"Get channel_id for {technology_name=}")

    technology.channel_id = get_channel_id(technology.name)

    logger.info(f"Writing {technology_name=} to database")

    write_technology_to_db(Technology.to_json(technology))

    return technology


def handle_tips_command(technology_name: str | None | UploadFile) -> str:
    logger.info("Handling tips command..")

    if not technology_name or not isinstance(technology_name, str):
        raise Exception("technology_name is required")

    logger.info(f"Find or create {technology_name=}")

    technology = create_technology(technology_name)

    if technology:
        logger.info(f"Created Technology {technology.name}")

        schedule_jobs(technology)

        logger.info("Saving job information")

        save_jobs()

        return f"We will give you tips and tricks about {technology.name} everyday on channel <#{technology.channel_id}>"
    return "An error occurred while registering the technology"


def handle_list_command() -> str:
    logger.info("Getting all channels")
    channel_list: list[Channel] = get_all_channel()

    logger.info("Formating channel links..")
    channel_links = [
        f"<#{channel.channel_id}>"
        for channel in channel_list
        if hasattr(channel, "channel_id")
    ]
    job_list = []

    logger.info("Formatting current job lists..")
    for job in schedule.jobs:
        next_run = job.next_run.strftime("%Y-%m-%d %H:%M:%S") if job.next_run else ""
        object_arg = job.job_func.args[0] if job.job_func else ""
        if getattr(object_arg, "object_type", ObjectType.BOOK) == ObjectType.BOOK:
            title = getattr(object_arg, "title", "Unknown")
        else:
            title = getattr(object_arg, "name", "Unknown")
        job_list.append(f"Next run: {next_run}, Title: {title}")
    channels_text = "\n".join(channel_links)
    jobs_text = "\n".join(job_list)
    return f"Channels I created:\n{channels_text}\n\nCurrent schedule:\n{jobs_text}"


def get_all_channel() -> list[Channel]:
    logger.info("Loading books for channels")

    books = load_books()

    logger.info("Loading techs for channels")

    technologies = load_technologies()

    return [Channel(channel_id=book.channel_id, name=book.title) for book in books] + [
        Channel(channel_id=tech.channel_id, name=tech.name) for tech in technologies
    ]
