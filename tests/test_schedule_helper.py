import schedule
import pytest
from unittest.mock import patch

from datetime import datetime
from src.constant import DEFAULT_SCHEDULE_TIME
from src.schedule_helper import schedule_jobs
from tests.test_utils import default_book_per_page


class TestScheduleJobs:
    def setup_method(self):
        schedule.clear()

    def test_raises_exception_if_no_book(self):
        with pytest.raises(Exception, match="Called scheduler without a valid object"):
            schedule_jobs(None)

    @patch("src.main.send_daily_book_summary")
    def test_schedules_job_when_book_provided(self, mock_send):
        book = default_book_per_page
        schedule_jobs(book)
        assert len(schedule.jobs) == 1
        job = schedule.jobs[0]
        assert job.job_func.func == mock_send
        assert job.job_func.args[0] == book
        assert (
            getattr(job, "at_time", None)
            == datetime.strptime(DEFAULT_SCHEDULE_TIME, "%H:%M").time()
        )
