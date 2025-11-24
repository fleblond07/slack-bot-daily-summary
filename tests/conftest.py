import psycopg2
import pytest

from src.constant import get_database_url
from src.db_helper import get_db_connection


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    try:
        conn = psycopg2.connect(get_database_url())
        conn.autocommit = True
        cursor = conn.cursor()

        cursor.execute("""
            DROP TABLE IF EXISTS channels CASCADE;
            DROP TABLE IF EXISTS items CASCADE;
            DROP TABLE IF EXISTS jobs CASCADE;
            DROP TABLE IF EXISTS books CASCADE;
            DROP TABLE IF EXISTS technologies CASCADE;
        """)

        cursor.close()
        conn.close()
    except psycopg2.OperationalError:
        pytest.skip("PostgreSQL database not available for testing")

    from src.db_helper import init_db

    init_db()

    yield

    try:
        conn = psycopg2.connect(get_database_url())
        conn.autocommit = True
        cursor = conn.cursor()

        cursor.execute("DELETE FROM channels")
        cursor.execute("DELETE FROM items")
        cursor.execute("DELETE FROM jobs")
        cursor.execute("DELETE FROM books")
        cursor.execute("DELETE FROM technologies")

        cursor.close()
        conn.close()
    except Exception:
        pass


@pytest.fixture(autouse=True)
def clean_database():
    yield
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM channels")
            cursor.execute("DELETE FROM items")
            cursor.execute("DELETE FROM jobs")
            cursor.execute("DELETE FROM books")
            cursor.execute("DELETE FROM technologies")
    except Exception:
        pass
