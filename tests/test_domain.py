from src.domain import Book, Channel, ChannelList, Type
from tests.test_utils import default_book_per_page, default_dict_from_json


class TestDomainType:
    def test_get_type_for_empty_dict_should_return_by_page(self):
        assert Type.get_type({}) == Type.BY_PAGE

    def test_get_type_for_dict_with_chapter_count_should_return_by_chapter(self):
        assert Type.get_type({"chapterCount": 23}) == Type.BY_CHAPTER


class TestDomainBook:
    def test_to_json_from_valid_book(self):
        book = default_book_per_page
        assert Book.to_json(book) == default_dict_from_json

    def test_from_json_to_valid_book(self):
        dict = default_dict_from_json
        assert Book.from_json(dict) == default_book_per_page


class TestDomainChannel:
    def setup_method(self):
        self.books = [
            {"channel_id": "12345", "name": "Toto"},
            {"channel_id": "67891", "name": "Tata"},
        ]
        self.default_channel = "102938"

        self.default_channel_list = ChannelList(
            data=[
                Channel(channel_id=book.get("channel_id"), book_name=book.get("name"))
                for book in self.books
            ],
        )

    def test_channel_list_from_domain_nullable(self):
        assert (
            ChannelList.from_domain(
                channel_list=[
                    Channel(channel_id="12345", book_name="Toto"),
                    Channel(channel_id="67891", book_name="Tata"),
                ]
            )
            == self.default_channel_list
        )

    def test_channel_list_from_string(self):
        expected_string = "List of channels: (Toto)[#12345]\n(Tata)[#67891]\n"
        assert ChannelList.to_string(self.default_channel_list) == expected_string
