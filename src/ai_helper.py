from typing import TYPE_CHECKING
from openai import Client, OpenAI
from dotenv import load_dotenv

if TYPE_CHECKING:
    from tests.test_utils import TestClient


load_dotenv()


def get_summary_for_book_by_page(
    title: str, author: str, target_page: int, current_page: int
) -> str:
    if not title or target_page <= 0 or current_page > target_page:
        raise Exception(
            f"Invalid value was given, aborting before sending request - Book name {title} - Page range {current_page} {target_page}"
        )
    prompt = f"Please make a summary of the pages {current_page} to {target_page} for the book {title} by {author} - This summary can be detailed, it should be able to be read in under five minutes - Please refrain from using emojis etc.. Only use headings if necessary, highlight the important words, phrases. Also I want your answer to ONLY CONTAIN THE SUMMARY, nothing else no hello or bye or question JUST the summary"
    return _send_prompt(prompt=prompt)


def get_summary_for_book_by_chapter(
    title: str, author: str, current_chapter: int
) -> str:
    if not title or current_chapter < 0:
        raise Exception(
            f"Invalid value was given, aborting before sending request - Book name {title} - Current chapter {current_chapter}"
        )
    prompt = f"Please make a summary of the chapter {current_chapter} of the book {title} by {author} - This summary should be detailed, it should be able to be read in under five minutes - Please refrain from using emojis etc.. use slack-flavored markdown for headers and highlighting the important words, phrases. Also I want your answer to ONLY CONTAIN THE SUMMARY, nothing else no hello or bye or question JUST the summary"
    return _send_prompt(prompt=prompt)


def get_summary_for_technology(technology_name: str) -> str:
    if not technology_name:
        raise Exception(
            f"Invalid value was given, aborting before send request {technology_name=}"
        )
    prompt = f"Please give me a tip or trick for using technology: {technology_name} - This tip or trick should be detailed with code example when necessary, Please refrain from using emojis etc.. use slack-flavored markdown for headers and highlighting the importan words, phrases. Also I want you answer to ONLY CONTAIN THE TIPS OR TRICKS, nothing else no hello or by or question JUST the tip"
    return _send_prompt(prompt=prompt)


def _send_prompt(prompt: str, client: "None | TestClient | Client" = None) -> str:
    client = client or OpenAI()
    if not prompt:
        raise Exception("Empty prompt was given, aborting before sending request")
    response = client.responses.create(model="gpt-4o-mini", input=prompt)
    return response.output_text
