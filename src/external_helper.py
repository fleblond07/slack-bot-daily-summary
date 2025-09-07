import requests
import os
from src.domain import Book, State, Type
from dotenv import load_dotenv

load_dotenv()


def get_book_information(isbn: str) -> Book:
    google_library_response = requests.get(f"{os.getenv('GOOGLE_API_URL')}isbn:{isbn}")
    if google_library_response.status_code == 200 and (
        google_library_response.json().get("totalItems", 0) > 0
    ):
        return _load_book_from_google(google_library_response.json())
    raise Exception(f"Couldnt find book with isbn: {isbn}")


def get_book_isbn(book_name: str) -> str:
    google_library_response = requests.get(
        f"{os.getenv('GOOGLE_API_URL')}intitle:{book_name}"
    )
    if google_library_response.status_code == 200 and (
        google_library_response.json().get("totalItems", 0) > 0
    ):
        return _extract_isbn(
            google_library_response.json().get("items")[0].get("volumeInfo")
        )
    raise Exception(f"Couldnt find book with name: {book_name}")


def _extract_isbn(volume_info: dict[str, list[dict]]) -> str:
    industry_identifiers = volume_info.get("industryIdentifiers", [])
    for identifier in industry_identifiers:
        if identifier.get("type") == "ISBN_13":
            return identifier.get("identifier", "")
    return ""


def _load_book_from_google(json: dict) -> Book:
    if (totalItems := json.get("totalItems", 0)) > 1:
        raise Exception(f"Multiple items found for the same ISBN - {totalItems}")
    book_information = json.get("items", {})[0].get("volumeInfo")
    return Book(
        isbn=_extract_isbn(book_information),
        title=book_information.get("title"),
        author=book_information.get("authors")[0],
        state=State.ON_GOING,
        type=Type.get_type(book_information),
        page_count=book_information.get("pageCount", 0),
        chapter_number=book_information.get("chapterCount", 0),
    )
