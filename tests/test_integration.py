from datetime import datetime
from fastapi.testclient import TestClient
from unittest.mock import patch
from db_helper import get_db_connection
from constant import DB_NAME, DEFAULT_SCHEDULE_TIME, JOBS_DB_NAME
import httpx
import schedule
from endpoint import app
from main import send_daily_book_summary, send_daily_tech_summary
from tests.test_utils import default_book_for_integration, default_tech_for_integation


client = TestClient(app)


class TestIntegrationTestBookHappyPath:
    def setup_method(self):
        self.jobs_db_name = JOBS_DB_NAME
        self.db_name = DB_NAME

        with get_db_connection(self.jobs_db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    isbn TEXT,
                    name TEXT
                )
            """)
            cursor.execute("DELETE FROM jobs WHERE 1=1")

        with get_db_connection(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    object_type TEXT NOT NULL,
                    object_id INTEGER NOT NULL,
                    UNIQUE(object_type, object_id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    isbn TEXT UNIQUE NOT NULL,
                    title TEXT,
                    author TEXT,
                    page_count INTEGER,
                    state TEXT,
                    type TEXT,
                    chapter_number INTEGER,
                    current_chapter INTEGER,
                    current_page INTEGER
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS technologies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS channels (
                    channel_id TEXT NOT NULL,
                    object_id INTEGER UNIQUE NOT NULL
                )
            """)
            cursor.execute("DELETE FROM channels WHERE 1=1")
            cursor.execute("DELETE FROM items WHERE 1=1")
            cursor.execute("DELETE FROM books WHERE 1=1")
            cursor.execute("DELETE FROM technologies WHERE 1=1")

        schedule.clear()

    @patch("main.get_channel_id")
    @patch("main.get_book_information")
    @patch("decorators.verify_slack_request")
    @patch("main.get_book_isbn")
    @patch("ai_helper._send_prompt")
    @patch("main.send_slack_message")
    def test_integration_book_happy_path(
        self,
        mock_send_slack,
        mock_gpt,
        mock_isbn,
        mock_verify_slack,
        mock_return_book,
        mock_get_channel,
    ):
        mock_verify_slack.return_value = True
        mock_isbn.return_value = "12345678"
        mock_return_book.return_value = default_book_for_integration
        mock_get_channel.return_value = "1234567"
        mock_gpt.return_value = "This is your daily summary of x"

        response: httpx.Response = client.post(
            "/slack/readme",
            data={"text": "Johnny McEngineer", "command": "/readme"},
        )
        assert response.status_code == 200
        assert response.json() == {
            "response_type": "in_channel",
            "text": "Johnny McEngineer will be summarized for you everyday a new chapter at 9am on channel <#1234567>",
        }

        assert len(schedule.jobs) == 1
        job = schedule.jobs[0]
        assert job.job_func.func == send_daily_book_summary
        assert job.job_func.args[0].isbn == default_book_for_integration.isbn
        assert (
            getattr(job, "at_time", None)
            == datetime.strptime(DEFAULT_SCHEDULE_TIME, "%H:%M").time()
        )

        job.run()

        assert mock_send_slack.call_count == 2
        mock_send_slack.assert_any_call("1234567", "This is your daily summary of x")
        mock_send_slack.assert_any_call(
            "1234567",
            "This was the final summary for Johnny McEngineer - Thank you for using the bot!",
        )


class TestIntegrationTestTechHappyPath:
    def setup_method(self):
        self.jobs_db_name = JOBS_DB_NAME
        self.db_name = DB_NAME

        with get_db_connection(self.jobs_db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    isbn TEXT,
                    name TEXT
                )
            """)
            cursor.execute("DELETE FROM jobs WHERE 1=1")

        with get_db_connection(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    object_type TEXT NOT NULL,
                    object_id INTEGER NOT NULL,
                    UNIQUE(object_type, object_id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    isbn TEXT UNIQUE NOT NULL,
                    title TEXT,
                    author TEXT,
                    page_count INTEGER,
                    state TEXT,
                    type TEXT,
                    chapter_number INTEGER,
                    current_chapter INTEGER,
                    current_page INTEGER
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS technologies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS channels (
                    channel_id TEXT NOT NULL,
                    object_id INTEGER UNIQUE NOT NULL
                )
            """)
            cursor.execute("DELETE FROM channels WHERE 1=1")
            cursor.execute("DELETE FROM items WHERE 1=1")
            cursor.execute("DELETE FROM books WHERE 1=1")
            cursor.execute("DELETE FROM technologies WHERE 1=1")

        schedule.clear()

    @patch("main.get_channel_id")
    @patch("decorators.verify_slack_request")
    @patch("ai_helper._send_prompt")
    @patch("main.send_slack_message")
    def test_integration_tech_happy_path(
        self,
        mock_send_slack,
        mock_gpt,
        mock_verify_slack,
        mock_get_channel,
    ):
        mock_verify_slack.return_value = True
        mock_get_channel.return_value = "1234567"
        mock_gpt.return_value = "This is your daily summary of x"

        response: httpx.Response = client.post(
            "/slack/tips",
            data={"text": "VueJS", "command": "/tips"},
        )
        assert response.status_code == 200
        assert response.json() == {
            "response_type": "in_channel",
            "text": "We will give you tips and tricks about VueJS everyday on channel <#1234567>",
        }

        assert len(schedule.jobs) == 1
        job = schedule.jobs[0]

        assert job.job_func.func == send_daily_tech_summary
        assert job.job_func.args[0].name == default_tech_for_integation.name
        assert (
            getattr(job, "at_time", None)
            == datetime.strptime(DEFAULT_SCHEDULE_TIME, "%H:%M").time()
        )

        job.run()

        mock_send_slack.assert_called_once_with(
            "1234567", "This is your daily summary of x"
        )
