from src.secrets_manager import get_secret

HEADING_MARKDOWN_REGEX = r"^#{1,6}\s*(.+)$"
BOLD_MARKDOWN_REGEX = r"\*\*(.+?)\*\*"
BOLD_SLACK_REGEX = r"*\1*"

MARKDOWN_RULES = [
    (HEADING_MARKDOWN_REGEX, BOLD_SLACK_REGEX),
    (BOLD_MARKDOWN_REGEX, BOLD_SLACK_REGEX),
]

DEFAULT_SCHEDULE_TIME = "09:30"
SCHEDULER_CHECK_INTERVAL_SECONDS = 60

SLACK_TIMESTAMP_MAX_AGE_SECONDS = 300


def get_database_url() -> str:
    db_host = get_secret("DB_HOST") or "localhost"
    db_port = get_secret("DB_PORT") or "5432"
    db_name = get_secret("DB_NAME") or "daily_learner"
    db_user = get_secret("DB_USER") or "postgres"
    db_password = get_secret("DB_PASSWORD") or "postgres"
    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


DEFAULT_PAGES_SPLIT = 15
GOOGLE_API_URL = "https://www.googleapis.com/books/v1/volumes?q="
