import schedule
from dotenv import load_dotenv
from src.domain import Book, Channel, State, Type
from tests.test_utils import (
    default_book_per_page_from_google,
    default_finished_book_per_page_from_google,
)
from src.main import (
    _get_pages_for_summary,
    create_book,
    get_all_channel,
    handle_list_command,
    handle_readme_command,
    send_daily_book_summary,
)
from unittest.mock import patch
import pytest

load_dotenv()


class TestGetPagesSummary:
    def setup_method(self):
        self.book = default_book_per_page_from_google

    def test_get_page_for_default_book(self):
        assert _get_pages_for_summary(book=self.book) == 8

    def test_get_page_for_current_book(self):
        self.book.current_page = 9
        assert _get_pages_for_summary(book=self.book) == 17

    def test_invalid_page_count(self):
        self.book.page_count = 0
        assert _get_pages_for_summary(book=self.book) == 9


class TestSendDailySummary:
    @patch("src.main.send_slack_message")
    @patch("src.main.get_summary_for_book_by_chapter")
    @patch("src.main.write_book_to_db")
    def test_by_chapter_book_happy_path(
        self, mock_write_db, mock_get_summary, mock_send_slack
    ):
        mock_get_summary.return_value = "chapter summary"

        book = Book(
            isbn="1234567812341",
            title="My Book",
            author="Author",
            channel_id="C123",
            type=Type.BY_CHAPTER,
            current_chapter=1,
            chapter_number=3,
            page_count=0,
            state=State.ON_GOING,
        )

        send_daily_book_summary(book)

        mock_get_summary.assert_called_once_with("My Book", "Author", 1)
        mock_send_slack.assert_any_call("C123", "chapter summary")
        mock_write_db.assert_called_once()
        assert book.current_chapter == 2
        assert book.state != State.FINISHED

    @patch("src.main.send_slack_message")
    @patch("src.main.get_summary_for_book_by_chapter")
    @patch("src.main.write_book_to_db")
    def test_by_chapter_book_last_chapter(
        self, mock_write_db, mock_get_summary, mock_send_slack
    ):
        mock_get_summary.return_value = "last summary"

        book = Book(
            isbn="1234567812341",
            title="My Book",
            author="Author",
            channel_id="C123",
            type=Type.BY_CHAPTER,
            current_chapter=2,
            chapter_number=3,
            page_count=0,
            state=State.ON_GOING,
        )

        send_daily_book_summary(book)

        mock_send_slack.assert_any_call("C123", "last summary")
        final_message = f"This was the final summary for {book.title} - Thank you for using the bot!"
        mock_send_slack.assert_any_call("C123", final_message)
        assert book.state == State.FINISHED

    @patch("src.main.send_slack_message")
    @patch("src.main.get_summary_for_book_by_page")
    @patch("src.main._get_pages_for_summary")
    @patch("src.main.write_book_to_db")
    def test_by_page_book_happy_path(
        self, mock_write_db, mock_get_pages, mock_get_summary, mock_send_slack
    ):
        mock_get_pages.return_value = 10
        mock_get_summary.return_value = "page summary"

        book = Book(
            isbn="1234567812341",
            title="My Book",
            author="Author",
            channel_id="C123",
            type=Type.BY_PAGE,
            current_page=5,
            page_count=20,
            state=State.ON_GOING,
        )

        send_daily_book_summary(book)

        mock_get_pages.assert_called_once_with(book)
        mock_get_summary.assert_called_once_with("My Book", "Author", 10, 5)
        mock_send_slack.assert_any_call("C123", "page summary")
        mock_write_db.assert_called_once()
        assert book.current_page == 10
        assert book.state != State.FINISHED

    @patch("src.main.send_slack_message")
    @patch("src.main.get_summary_for_book_by_page")
    @patch("src.main._get_pages_for_summary")
    @patch("src.main.write_book_to_db")
    def test_by_page_book_last_page(
        self, mock_write_db, mock_get_pages, mock_get_summary, mock_send_slack
    ):
        mock_get_pages.return_value = 100
        mock_get_summary.return_value = "final page summary"

        book = Book(
            isbn="1234567812341",
            title="My Book",
            author="Author",
            channel_id="C123",
            type=Type.BY_PAGE,
            current_page=99,
            page_count=100,
            state=State.ON_GOING,
        )

        send_daily_book_summary(book)

        final_message = f"This was the final summary for {book.title} - Thank you for using the bot!"
        mock_send_slack.assert_any_call("C123", "final page summary")
        mock_send_slack.assert_any_call("C123", final_message)
        assert book.state == State.FINISHED

    @patch("src.main.get_summary_for_book_by_chapter")
    def test_summary_returns_none_should_raise_exception(self, mock_get_summary):
        mock_get_summary.return_value = None

        book = Book(
            isbn="1234567812341",
            title="My Book",
            author="Author",
            channel_id="C123",
            type=Type.BY_CHAPTER,
            current_chapter=1,
            chapter_number=2,
            page_count=0,
            state=State.ON_GOING,
        )

        with pytest.raises(Exception) as exc:
            send_daily_book_summary(book)

        assert f"An error occured getting the summary for book {book.title}" in str(
            exc.value
        )


class TestCreateBook:
    def setup_method(self):
        self.on_going_book = default_book_per_page_from_google
        self.finished_book = default_finished_book_per_page_from_google

    @patch("src.main.get_book_isbn")
    def test_no_isbn_should_raise_exception(self, mock_get_isbn):
        mock_get_isbn.return_value = None

        with pytest.raises(Exception) as exc:
            create_book("SomeBook")

        assert "Cannot find ISBN" in str(exc.value)

    @patch("src.main.get_book_isbn")
    @patch("src.main.load_book_by_isbn")
    def test_book_already_finished_should_raise_exception(
        self, mock_load_book, mock_get_isbn
    ):
        mock_get_isbn.return_value = "12345"
        mock_load_book.return_value = self.finished_book

        with pytest.raises(Exception) as exc:
            create_book("SomeBook")

        assert (
            "This book was already completed - Check the channels for the books summary"
            in str(exc.value)
        )

    @patch("src.main.get_book_isbn")
    @patch("src.main.load_book_by_isbn")
    def test_book_already_exists_and_not_finished_should_return_book(
        self, mock_load_book, mock_get_isbn
    ):
        mock_get_isbn.return_value = "12345"
        mock_load_book.return_value = self.on_going_book

        book, msg = create_book("SomeBook")

        assert book is self.on_going_book
        assert msg == ""

    @patch("src.main.write_book_to_db")
    @patch("src.main.get_channel_id")
    @patch("src.main.get_book_information")
    @patch("src.main.load_book_by_isbn")
    @patch("src.main.get_book_isbn")
    def test_new_book_created_and_written_to_db(
        self,
        mock_get_isbn,
        mock_load_book,
        mock_get_info,
        mock_get_channel,
        mock_write_db,
    ):
        mock_get_isbn.return_value = "12345"
        mock_load_book.return_value = None

        mock_get_info.return_value = self.on_going_book
        mock_get_channel.return_value = "123456"

        book, msg = create_book("SomeBook")

        mock_get_info.assert_called_once_with("12345")
        mock_get_channel.assert_called_once_with("Clean Code")
        mock_write_db.assert_called_once()
        assert self.on_going_book.channel_id == "123456"
        assert msg == ""


class TestHandleReadmeCommand:
    def test_invalid_book_name_type_should_raise(self):
        with pytest.raises(Exception) as exc:
            handle_readme_command(None)
        assert "Invalid book_name type given" in str(exc.value)

    @patch("src.main.create_book")
    def test_create_book_returns_error_string(self, mock_create):
        mock_create.return_value = (None, "some error")

        result = handle_readme_command("MyBook")
        assert result == "some error"

    @patch("src.main.save_jobs")
    @patch("src.main.create_book")
    def test_create_book_returns_valid_book(self, mock_create, mock_schedule):
        book = default_book_per_page_from_google
        mock_create.return_value = (book, "")

        result = handle_readme_command("MyBook")

        mock_schedule.assert_called_once()

        assert (
            result
            == f"{book.title} will be summarized for you everyday a new chapter at 9am on channel <#{book.channel_id}>"
        )

    @patch("src.main.create_book")
    def test_create_book_returns_none_book(self, mock_create):
        mock_create.return_value = (None, "")

        result = handle_readme_command("MyBook")
        assert result == "An error occured while registering the book"


class TestHandleListCommand:
    @patch("src.main.get_all_channel")
    def test_no_channels_should_return_error(self, mock_get_channels):
        mock_get_channels.return_value = []

        result = handle_list_command()
        assert result == "An error occured when fetching the channel list"

    @patch("src.main.get_all_channel")
    def test_channels_no_jobs(self, mock_get_channels):
        schedule.clear()
        mock_get_channels.return_value = [
            Channel(channel_id="C123", book_name="My Book"),
            Channel(channel_id="C456", book_name="Clean Code"),
        ]

        result = handle_list_command()

        assert "Channels I created:" in result
        assert "<#C123>" in result
        assert "<#C456>" in result
        assert "Current schedule:" in result
        assert result.strip().endswith("Current schedule:")

    @patch("src.main.get_all_channel")
    def test_channels_with_jobs(self, mock_get_channels):
        mock_get_channels.return_value = [
            Channel(channel_id="C123", book_name="My Book")
        ]

        book = default_book_per_page_from_google

        def dummy_job(b):
            return b.title

        schedule.every().day.at("07:00").do(dummy_job, book)

        result = handle_list_command()

        assert "<#C123>" in result
        assert "Next run:" in result
        assert "Clean Code" in result


class TestGetAllChannel:
    @patch("src.main.load_books")
    def test_no_books_should_return_empty_list(self, mock_load_books):
        mock_load_books.return_value = []

        result = get_all_channel()
        assert result == []

    @patch("src.main.load_books")
    def test_books_should_return_channel_objects(self, mock_load_books):
        book1 = default_book_per_page_from_google
        book2 = default_finished_book_per_page_from_google

        mock_load_books.return_value = [book1, book2]

        result = get_all_channel()

        assert isinstance(result[0], Channel)
        assert result[0].channel_id == "123456"
        assert result[0].book_name == "Clean Code"

        assert isinstance(result[1], Channel)
        assert result[1].channel_id == "7891011"
        assert result[1].book_name == "The Clean Coder"
