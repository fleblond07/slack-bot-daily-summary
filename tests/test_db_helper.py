from tinydb import TinyDB, Query
import os
from src.main import send_daily_book_summary, send_daily_tech_summary
from src.db_helper import (
    load_book_by_isbn,
    load_books,
    load_jobs,
    load_technology_by_name,
    reset_jobs,
    save_book_jobs,
    save_tech_jobs,
    write_book_to_db,
    write_technology_to_db,
)
from tests.test_utils import (
    default_dict_from_json,
    default_technology,
    default_technology_from_json,
    second_technology_from_json,
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


class TestLoadTechnologyByName:
    def setup_method(self):
        self.db = TinyDB(os.getenv("DB_NAME", "books.json"))
        self.db.upsert(
            default_technology_from_json,
            Query().name == default_technology_from_json.get("name"),
        )

    def test_get_specific_technology(self):
        assert (
            load_technology_by_name(default_technology_from_json.get("name", ""))
            == default_technology
        )

    def test_get_unknown_technology(self):
        assert load_technology_by_name("unexisting") is None

    def test_get_technology_with_no_name_given(self):
        with pytest.raises(Exception) as exception:
            assert load_technology_by_name(technology_name="")
        assert str(exception.value) == "Empty technology name given"


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


class TestWriteTechnologyToJSON:
    def setup_method(self):
        self.db = TinyDB(os.getenv("DB_NAME", "books.json"))
        self.db.upsert(
            default_technology_from_json,
            Query().name == default_technology_from_json.get("name"),
        )

    def test_write_empty_book_to_json_should_raise_exception(self):
        with pytest.raises(Exception) as exception:
            write_technology_to_db(technology={})
        assert str(exception.value) == "Invalid technology given"

    def test_write_valid_book_to_json(self):
        write_technology_to_db(technology=second_technology_from_json)
        result = self.db.search(Query().name == second_technology_from_json.get("name"))
        assert result[0] == second_technology_from_json

    def test_update_valid_book_to_json(self):
        updated_dict = default_technology_from_json.copy()
        updated_dict["name"] = "Go"
        write_technology_to_db(technology=updated_dict)
        result = self.db.search(Query().name == updated_dict.get("name"))
        assert result[0] == updated_dict


class TestLoadJobs:
    def setup_method(self):
        self.db = TinyDB(os.getenv("JOBS_DB_NAME", "test.json"))
        self.db.truncate()
        self.db.insert(
            {
                "isbn": "49837410934324",
                "object_type": "book",
            },
        )
        self.db.insert(
            {"name": "SQLAlchemy", "object_type": "tech"},
        )

    def test_loads_jobs_into_schedule(self):
        schedule.clear()
        load_jobs()

        assert len(schedule.jobs) == 2
        for job in schedule.jobs:
            assert job.job_func.__name__ in [
                "send_daily_book_summary",
                "send_daily_tech_summary",
            ]


class TestSaveJobs:
    def _test_job(self) -> None:
        pass

    def setup_method(self):
        self.db = TinyDB(os.getenv("JOBS_DB_NAME", "test.json"))

    def test_saves_book_jobs_from_schedule(self):
        schedule.clear()
        schedule.every(1).seconds.do(send_daily_book_summary, default_book_per_page)

        save_book_jobs()
        jobs = self.db.all()
        inserted_job = jobs[0]
        assert inserted_job["isbn"] == default_book_per_page.isbn

    def test_saves_tech_jobs_from_schedule(self):
        schedule.clear()
        schedule.every(1).seconds.do(send_daily_tech_summary, default_technology)

        save_tech_jobs()
        jobs = self.db.all()
        inserted_job = jobs[0]
        assert inserted_job["name"] == default_technology.name


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
