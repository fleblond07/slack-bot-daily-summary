import responses
from src.external_helper import (
    _extract_isbn,
    _load_book_from_google,
    get_book_information,
    get_book_isbn,
)
import pytest
from tests.test_utils import (
    default_google_response_per_page,
    default_book_per_page_from_google,
    default_google_get_responses,
    google_by_name_get_responses_with_bad_status_code,
    google_by_name_get_responses_with_item,
    google_by_name_get_responses_with_no_items,
    google_get_responses_with_bad_status_code,
    google_get_responses_with_no_items,
)


class TestExtractISBN:
    def test_extract_isbn_from_empty_dict_should_return_empty_string(self):
        assert _extract_isbn({"industryIdentifiers": []}) == ""

    def test_extract_isbn_from_good_dict_should_return_isbn(self):
        assert (
            _extract_isbn(
                {
                    "industryIdentifiers": [
                        {"identifier": "1234567891", "type": "ISBN_10"},
                        {"type": "ISBN_13", "identifier": "1234567891234"},
                    ]
                }
            )
            == "1234567891234"
        )


class TestLoadBookFromGoogle:
    def test_load_book_with_multiple_items_should_raise_exception(self):
        with pytest.raises(Exception) as exception:
            _load_book_from_google({"totalItems": 3})
        assert str(exception.value) == "Multiple items found for the same ISBN - 3"

    def test_load_book_with_good_dict_should_return_book(self):
        actual_book = _load_book_from_google(default_google_response_per_page)
        assert actual_book == default_book_per_page_from_google


class TestGetBookInformation:
    @responses.activate
    def test_books_with_no_items_should_raise_exception(self):
        google_get_responses_with_no_items()
        with pytest.raises(Exception) as exception:
            get_book_information("123456")
        assert str(exception.value) == "Couldnt find book with isbn: 123456"

    @responses.activate
    def test_books_with_bad_status_code_should_raise_exception(self):
        google_get_responses_with_bad_status_code()
        with pytest.raises(Exception) as exception:
            get_book_information("1234567")
        assert str(exception.value) == "Couldnt find book with isbn: 1234567"

    @responses.activate
    def test_good_response_should_return_book(self):
        default_google_get_responses()
        assert (
            get_book_information("9780140328721") == default_book_per_page_from_google
        )


class TestGetBookISBN:
    @responses.activate
    def test_books_with_no_items_should_raise_exception(self):
        google_by_name_get_responses_with_no_items()
        with pytest.raises(Exception) as exception:
            get_book_isbn("SomeBook")
        assert str(exception.value) == "Couldnt find book with name: SomeBook"

    @responses.activate
    def test_books_with_bad_status_code_should_raise_exception(self):
        google_by_name_get_responses_with_bad_status_code()
        with pytest.raises(Exception) as exception:
            get_book_isbn("SomeBook")
        assert str(exception.value) == "Couldnt find book with name: SomeBook"

    @responses.activate
    def test_good_response_should_return_isbn(self):
        google_by_name_get_responses_with_item()
        assert get_book_isbn("SomeBook") == "9780140328721"
