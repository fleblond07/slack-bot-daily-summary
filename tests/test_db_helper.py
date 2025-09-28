from tinydb import TinyDB, Query
import os
from src.main import send_daily_book_summary
from src.db_helper import (
    load_book_by_isbn,
    load_books,
    load_jobs,
    reset_jobs,
    save_jobs,
    write_book_to_db,
)
from tests.test_utils import (
    default_dict_from_json,
    second_book_json,
    default_book_per_page,
)
import pytest
import schedule


class TestLoadBooks:
    def setup_method(self):
        self.db = TinyDB(os.getenv("DB_NAME", "books.json"))
        self.db.upsert(
            default_dict_from_json, Query().isbn == default_dict_from_json.get("isbn")
        )

    def test_open_default_book(self):
        assert default_book_per_page in load_books()


class TestLoadBookByISBN:
    def setup_method(self):
        self.db = TinyDB(os.getenv("DB_NAME", "books.json"))
        self.db.upsert(
            default_dict_from_json, Query().isbn == default_dict_from_json.get("isbn")
        )

    def test_get_specific_book(self):
        assert (
            load_book_by_isbn(default_dict_from_json.get("isbn", ""))
            == default_book_per_page
        )

    def test_get_unknown_book(self):
        assert load_book_by_isbn("unexisting") is None

    def test_get_book_with_no_isbn_given(self):
        with pytest.raises(Exception) as exception:
            assert load_book_by_isbn(isbn="")
        assert str(exception.value) == "Empty isbn given"


class TestWriteBookToJSON:
    def setup_method(self):
        self.db = TinyDB(os.getenv("DB_NAME", "books.json"))
        self.db.upsert(
            default_dict_from_json, Query().isbn == default_dict_from_json.get("isbn")
        )

    def test_write_empty_book_to_json_should_raise_exception(self):
        with pytest.raises(Exception) as exception:
            write_book_to_db(book={})
        assert str(exception.value) == "Empty book was given"

    def test_write_valid_book_to_json(self):
        write_book_to_db(book=second_book_json)
        result = self.db.search(Query().isbn == second_book_json.get("isbn"))
        assert result[0] == second_book_json

    def test_update_valid_book_to_json(self):
        updated_dict = default_dict_from_json.copy()
        updated_dict["state"] = "finished"
        write_book_to_db(book=updated_dict)
        result = self.db.search(Query().isbn == updated_dict.get("isbn"))
        assert result[0] == updated_dict


class TestLoadJobs:
    def setup_method(self):
        self.db = TinyDB(os.getenv("JOBS_DB_NAME", "test.json"))
        self.db.truncate()
        self.db.insert(
            {
                "isbn": "49837410934324",
                "object_type": "book",
            }
        )

    def test_loads_jobs_into_schedule(self):
        schedule.clear()
        load_jobs()

        assert len(schedule.jobs) == 1
        job = schedule.jobs[0]
        assert job.job_func.__name__ == "send_daily_book_summary"


class TestSaveJobs:
    def _test_job(self) -> None:
        pass

    def setup_method(self):
        self.db = TinyDB(os.getenv("JOBS_DB_NAME", "test.json"))

    def test_saves_jobs_from_schedule(self):
        schedule.clear()
        schedule.every(1).seconds.do(send_daily_book_summary, default_book_per_page)

        save_jobs()
        jobs = self.db.all()
        inserted_job = jobs[0]
        assert inserted_job["isbn"] == default_book_per_page.isbn


class TestResetJobs:
    def _test_job(self) -> None:
        pass

    def setup_method(self):
        self.db = TinyDB(os.getenv("JOBS_DB_NAME", "test.json"))

    def test_resets_jobs_and_db(self):
        schedule.clear()
        schedule.every(1).seconds.do(self._test_job, "world")
        assert schedule.jobs

        reset_jobs()
        assert len(schedule.jobs) == 0
        jobs = self.db.all()
        assert len(jobs) == 0
