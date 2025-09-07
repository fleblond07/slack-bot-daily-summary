from src.ai_helper import (
    _send_prompt,
    get_summary_for_book_by_chapter,
    get_summary_for_book_by_page,
)
import pytest
from unittest.mock import patch
from tests.test_utils import TestClient


class TestAiHelper:
    def test_send_good_prompt_should_return_good_prompt(self):
        prompt = (
            'This is a test prompt, answer only with the word "TEST OK" nothing else'
        )
        result = _send_prompt(prompt=prompt, client=TestClient())
        assert result == "TEST OK"

    def test_empty_prompt_should_raise_exception(self):
        with pytest.raises(Exception) as exception:
            _send_prompt(prompt="", client=TestClient())
        assert (
            str(exception.value)
            == "Empty prompt was given, aborting before sending request"
        )

    def test_get_summary_for_book_by_chapter_should_call_a_correct_prompt(self):
        expected_prompt = "Please make a summary of the chapter 3 of the book MyTest by John - This summary should be detailed, it should be able to be read in under five minutes - Please refrain from using emojis etc.. use slack-flavored markdown for headers and highlighting the important words, phrases. Also I want your answer to ONLY CONTAIN THE SUMMARY, nothing else no hello or bye or question JUST the summary"

        with patch("src.ai_helper._send_prompt") as mock_send_prompt:
            mock_send_prompt.return_value = "TEST OK"

            get_summary_for_book_by_chapter("MyTest", "John", 3)

            mock_send_prompt.assert_called_once_with(prompt=expected_prompt)

    @pytest.mark.parametrize(
        "book_name, author, chapter", [("", "", 1), ("MyBook", "John", -1)]
    )
    def test_get_summary_for_book_by_chapter_with_invalid_chapter_should_raise_exception(
        self, book_name, author, chapter
    ):
        with pytest.raises(Exception) as exception:
            get_summary_for_book_by_chapter(book_name, author, chapter)
        assert (
            str(exception.value)
            == f"Invalid value was given, aborting before sending request - Book name {book_name} - Current chapter {chapter}"
        )

    @pytest.mark.parametrize(
        "title, author, target_page, current_page",
        [
            ("", "John", 1, 2),
            ("MyBook", "McCassidy", 0, 0),
            ("MyBook", "Michel", 23, 32),
        ],
    )
    def test_get_summary_for_book_by_page_with_invalid_chapter_should_raise_exception(
        self, title, author, target_page, current_page
    ):
        with pytest.raises(Exception) as exception:
            get_summary_for_book_by_page(title, author, target_page, current_page)
        assert (
            str(exception.value)
            == f"Invalid value was given, aborting before sending request - Book name {title} - Page range {current_page} {target_page}"
        )

    def test_get_summary_for_book_by_page_should_call_a_correct_prompt(self):
        expected_prompt = "Please make a summary of the pages 23 to 32 for the book MyBook by John - This summary can be detailed, it should be able to be read in under five minutes - Please refrain from using emojis etc.. Only use headings if necessary, highlight the important words, phrases. Also I want your answer to ONLY CONTAIN THE SUMMARY, nothing else no hello or bye or question JUST the summary"

        with patch("src.ai_helper._send_prompt") as mock_send_prompt:
            mock_send_prompt.return_value = "TEST OK"

            get_summary_for_book_by_page("MyBook", "John", 32, 23)

            mock_send_prompt.assert_called_once_with(prompt=expected_prompt)
