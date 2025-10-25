import schedule
import pytest
from unittest.mock import MagicMock, patch

from datetime import datetime
from src.constant import DEFAULT_SCHEDULE_TIME
from src.schedule_helper import (
    schedule_jobs,
    run_all_jobs,
    cancel_job_by_isbn,
    cancel_job_by_name,
)
from tests.test_utils import default_book_per_page, default_technology


class TestScheduleJobs:
    def setup_method(self):
        schedule.clear()

    def test_raises_exception_if_no_book(self):
        with pytest.raises(Exception, match="Called scheduler without a valid object"):
            schedule_jobs(None)

    def test_schedules_job_when_book_provided(self):
        from src.schedule_helper import _send_book_summary_by_isbn

        book = default_book_per_page
        schedule_jobs(book)
        assert len(schedule.jobs) == 1
        job = schedule.jobs[0]
        assert job.job_func.func == _send_book_summary_by_isbn
        assert job.job_func.args[0] == book.isbn
        assert (
            getattr(job, "at_time", None)
            == datetime.strptime(DEFAULT_SCHEDULE_TIME, "%H:%M").time()
        )


class TestRunJobs:
    @patch("src.schedule_helper.threading.Thread")
    @patch("src.schedule_helper.schedule.run_all")
    def test_run_all_jobs_starts_thread(
        self, mock_run_all: MagicMock, mock_thread_class: MagicMock
    ):
        mock_thread_instance = MagicMock()
        mock_thread_class.return_value = mock_thread_instance

        run_all_jobs()

        mock_thread_class.assert_called_once_with(
            name="Run all scheduled jobs", target=mock_run_all
        )
        mock_thread_instance.start.assert_called_once()


class TestCancelJobByIsbn:
    def setup_method(self):
        schedule.clear()

    def test_cancels_job_when_isbn_found(self):
        from src.schedule_helper import _send_book_summary_by_isbn

        book = default_book_per_page
        schedule.every().day.at(DEFAULT_SCHEDULE_TIME).do(
            _send_book_summary_by_isbn, book.isbn
        )

        assert len(schedule.jobs) == 1
        cancel_job_by_isbn(book.isbn)
        assert len(schedule.jobs) == 0

    def test_does_not_crash_when_isbn_not_found(self):
        cancel_job_by_isbn("non-existent-isbn")
        assert len(schedule.jobs) == 0


class TestCancelJobByName:
    def setup_method(self):
        schedule.clear()

    def test_cancels_job_when_name_found(self):
        from src.schedule_helper import _send_tech_summary_by_name

        tech = default_technology
        schedule.every().day.at(DEFAULT_SCHEDULE_TIME).do(
            _send_tech_summary_by_name, tech.name
        )

        assert len(schedule.jobs) == 1
        cancel_job_by_name(tech.name)
        assert len(schedule.jobs) == 0

    def test_does_not_crash_when_name_not_found(self):
        cancel_job_by_name("non-existent-tech")
        assert len(schedule.jobs) == 0
