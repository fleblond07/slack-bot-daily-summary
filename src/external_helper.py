import requests
from src.domain import Book, State, Type
from src.constant import GOOGLE_API_URL
import logging

logger = logging.getLogger("daily_learner")


def get_book_information(isbn: str) -> Book:
    logger.info(f"Getting book information from Google with {isbn=}")

    google_library_response = requests.get(f"{GOOGLE_API_URL}isbn:{isbn}")

    if google_library_response.status_code == 200 and (
        google_library_response.json().get("totalItems", 0) > 0
    ):
        logger.info("Successful response, loading book from google")
        return _load_book_from_google(google_library_response.json())

    logger.warning(
        f"An invalid response from Google was received: {google_library_response.status_code} - {google_library_response.content}"
    )
    raise Exception(f"Couldnt find book with {isbn=}")


def get_book_isbn(book_name: str) -> str:
    logger.info(f"Getting book information from Google with {book_name=}")

    google_library_response = requests.get(f"{GOOGLE_API_URL}intitle:{book_name}")

    if google_library_response.status_code == 200 and (
        google_library_response.json().get("totalItems", 0) > 0
    ):
        logger.info("Successful response, extracting isbn from google")
        return _extract_isbn(
            google_library_response.json().get("items")[0].get("volumeInfo")
        )

    logger.warning(
        f"An invalid response from Google was received: {google_library_response.status_code} - {google_library_response.content}"
    )

    raise Exception(f"Couldnt find book with name: {book_name}")


def _extract_isbn(volume_info: dict[str, list[dict]]) -> str:
    logger.info("Extracting ISBN from Google dict")

    industry_identifiers = volume_info.get("industryIdentifiers", [])
    for identifier in industry_identifiers:
        if identifier.get("type") == "ISBN_13":
            logger.info("Successfully found ISBN_13")
            return identifier.get("identifier", "")

    logger.warning(
        f"ISBN was not found for dict {volume_info.get('industryIdentifiers')}"
    )

    return ""


def _load_book_from_google(json: dict) -> Book:
    logger.info("Loading book from google response")

    if (total_items := json.get("totalItems", 0)) > 1:
        raise Exception(f"Multiple items found for the same ISBN - {total_items}")

    book_information = json.get("items", {})[0].get("volumeInfo")

    authors = book_information.get("authors", [])
    author = authors[0] if authors else "Unknown Author"

    return Book(
        isbn=_extract_isbn(book_information),
        title=book_information.get("title"),
        author=author,
        state=State.ON_GOING,
        type=Type.get_type(book_information),
        page_count=book_information.get("pageCount", 0),
        chapter_number=book_information.get("chapterCount", 0),
    )
