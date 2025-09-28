from src.domain import Book, ObjectType, State, Technology, Type
import os
import responses
from dotenv import load_dotenv

load_dotenv()


class TestClient:
    def chat_postMessage(self, channel: str, text: str):
        class FakeSlackResponse:
            ok = True

            def validate(self):
                return True

        return FakeSlackResponse()

    def conversations_list(self, types):
        return {
            "ok": True,
            "channels": [
                {"name": "toto", "id": "wrong_id"},
                {"name": "tata", "id": "123456"},
            ],
        }

    def conversations_create(self, name):
        return {"channel": {"id": "123456"}}

    class responses:
        @staticmethod
        def create(model, input):
            class FakeResponse:
                output_text = "TEST OK"

            return FakeResponse()


default_google_response_per_page = {
    "totalItems": 1,
    "items": [
        {
            "volumeInfo": {
                "title": "Clean Code",
                "authors": ["ThatGuy", "EverybodyHates"],
                "pageCount": 123,
                "industryIdentifiers": [
                    {"type": "ISBN_10", "identifier": "1234567891"},
                    {"type": "ISBN_13", "identifier": "9780140328721"},
                ],
            },
        }
    ],
}


default_book_per_page_from_google = Book(
    isbn="9780140328721",
    title="Clean Code",
    author="ThatGuy",
    state=State.ON_GOING,
    type=Type.BY_PAGE,
    page_count=123,
    channel_id="123456",
)

default_finished_book_per_page_from_google = Book(
    isbn="9780140328721",
    title="The Clean Coder",
    author="ThatGuy",
    state=State.FINISHED,
    type=Type.BY_PAGE,
    page_count=123,
    channel_id="7891011",
)


default_book_per_page = Book(
    isbn="9780140328721",
    title="Clean Code",
    author="ThatGuy",
    state=State.ON_GOING,
    type=Type.BY_PAGE,
    page_count=123,
    channel_id="123456",
)


default_dict_from_json = {
    "isbn": "9780140328721",
    "title": "Clean Code",
    "author": "ThatGuy",
    "state": "on_going",
    "type": "by_page",
    "object_type": "book",
    "page_count": 123,
    "chapter_number": 0,
    "current_chapter": 0,
    "current_page": 0,
    "channel_id": "123456",
}

default_technology_from_json = {
    "name": "SQLAlchemy",
    "object_type": "tech",
    "channel_id": "123456",
}

default_technology = Technology(
    name="SQLAlchemy", channel_id="123456", object_type=ObjectType.TECH
)

second_technology_from_json = {
    "name": "Python",
    "object_type": "tech",
    "channel_id": "7891011",
}

second_book_json = {
    "isbn": "49837410934324",
    "title": "The Clean Coder",
    "author": "ThatGuy",
    "state": "finished",
    "type": "by_chapter",
    "object_type": "book",
    "page_count": 456,
    "chapter_number": 0,
    "current_chapter": 0,
    "current_page": 0,
    "channel_id": "78910",
}

google_json_response = {
    "totalItems": 1,
    "items": [
        {
            "id": "DlQbmJc5WlQC",
            "volumeInfo": {
                "title": "Clean Code",
                "authors": ["ThatGuy", "EverybodyHates"],
                "publisher": "Puffin",
                "publishedDate": "1988",
                "description": "In this book you will find: Boggis an enormously fat man, a chicken farmer and a mean man. Bunce, a pot bellied dwarf, a duck-and-goose farmer and a nasty man. Bean, a thin man, a turkey-and-apple farmer and a beastly man. Badger, the most respectable and well-behaved animal in the district. Rat, a rude creature and a drunkard, and also a Mrs. Fox and her four children.",
                "industryIdentifiers": [
                    {"type": "ISBN_10", "identifier": "0140328726"},
                    {"type": "ISBN_13", "identifier": "9780140328721"},
                ],
                "readingModes": {"text": False, "image": False},
                "pageCount": 123,
                "printType": "BOOK",
                "categories": ["Juvenile Fiction"],
                "maturityRating": "NOT_MATURE",
                "allowAnonLogging": False,
                "contentVersion": "0.5.2.0.preview.0",
                "panelizationSummary": {
                    "containsEpubBubbles": False,
                    "containsImageBubbles": False,
                },
                "language": "en",
            },
        }
    ],
}


def default_google_get_responses():
    responses.add(
        responses.GET,
        f"{os.getenv('GOOGLE_API_URL')}isbn:9780140328721",
        json=google_json_response,
        status=200,
    )


def google_get_responses_with_no_items():
    responses.add(
        responses.GET,
        f"{os.getenv('GOOGLE_API_URL')}isbn:123456",
        json={"totalItems": 0},
        status=200,
    )


def google_get_responses_with_bad_status_code():
    responses.add(
        responses.GET,
        f"{os.getenv('GOOGLE_API_URL')}isbn:1234567",
        status=403,
    )


def google_by_name_get_responses_with_no_items():
    responses.add(
        responses.GET,
        f"{os.getenv('GOOGLE_API_URL')}intitle:SomeBook",
        json={"totalItems": 0, "items": []},
        status=200,
    )


def google_by_name_get_responses_with_bad_status_code():
    responses.add(
        responses.GET,
        f"{os.getenv('GOOGLE_API_URL')}intitle:SomeBook",
        json={},
        status=500,
    )


def google_by_name_get_responses_with_item():
    responses.add(
        responses.GET,
        f"{os.getenv('GOOGLE_API_URL')}intitle:SomeBook",
        json={
            "totalItems": 1,
            "items": [
                {
                    "volumeInfo": {
                        "title": "SomeBook",
                        "industryIdentifiers": [
                            {"type": "ISBN_13", "identifier": "9780140328721"}
                        ],
                    }
                }
            ],
        },
        status=200,
    )
