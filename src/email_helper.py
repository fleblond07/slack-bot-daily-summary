import logging
import smtplib
import traceback
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Protocol

import mistune

from src.secrets_manager import get_secret

logger = logging.getLogger("daily_learner")


class EmailClient(Protocol):
    def sendmail(self, from_addr: str, to_addrs: list[str], msg: str) -> dict: ...

    def quit(self) -> None: ...


def send_email(
    recipient: str,
    subject: str,
    message: str,
    client: EmailClient | None = None,
) -> bool:
    try:
        if not recipient or not subject or not message:
            raise Exception(
                f"Missing required arguments: {recipient=},{subject=},{bool(message)=}"
            )

        logger.info(f"Sending email to {recipient=}")

        from_email = get_secret("SMTP_FROM_EMAIL")
        if not from_email:
            raise Exception("SMTP_FROM_EMAIL secret not configured")

        msg = MIMEMultipart("alternative")
        msg["From"] = from_email
        msg["To"] = recipient
        msg["Subject"] = subject

        text_part = MIMEText(message, "plain")
        html_part = MIMEText(_markdown_to_html(message), "html")

        msg.attach(text_part)
        msg.attach(html_part)

        if client:
            logger.info("Using provided email client")
            client.sendmail(msg["From"], [recipient], msg.as_string())
            return True

        logger.info("Creating SMTP connection...")
        smtp_server = get_secret("SMTP_SERVER")
        if not smtp_server:
            raise Exception("SMTP_SERVER secret not configured")

        smtp_port_str = get_secret("SMTP_PORT")
        if not smtp_port_str:
            raise Exception("SMTP_PORT secret not configured")
        smtp_port = int(smtp_port_str)

        smtp_username = get_secret("SMTP_USERNAME")
        if not smtp_username:
            raise Exception("SMTP_USERNAME secret not configured")

        smtp_password = get_secret("SMTP_PASSWORD")
        if not smtp_password:
            raise Exception("SMTP_PASSWORD secret not configured")

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            logger.info("Starting TLS...")
            server.starttls()

            logger.info("Logging in to SMTP server...")
            server.login(smtp_username, smtp_password)

            logger.info("Sending email...")
            server.sendmail(msg["From"], [recipient], msg.as_string())

        logger.info("Email sent successfully")
        return True

    except Exception as e:
        logger.warning(traceback.format_exc())
        raise Exception(f"Error sending email: {str(e)}")


def _markdown_to_html(message: str) -> str:
    if not message:
        raise Exception("Empty message given")

    logger.info("Processing markdown to HTML...")

    markdown = mistune.create_markdown()
    html_content = markdown(message)

    html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            {html_content}
        </body>
    </html>
    """

    return html
