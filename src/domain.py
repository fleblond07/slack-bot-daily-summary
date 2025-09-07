from dataclasses import dataclass
from enum import Enum
import os
from dotenv import load_dotenv

load_dotenv()


class State(Enum):
    FINISHED = "finished"
    ON_GOING = "on_going"


class Type(Enum):
    BY_CHAPTER = "by_chapter"
    BY_PAGE = "by_page"

    @staticmethod
    def get_type(book_information: dict) -> "Type":
        if book_information.get("chapterCount"):
            return Type.BY_CHAPTER
        return Type.BY_PAGE


@dataclass
class Channel:
    channel_id: str | None
    book_name: str | None


@dataclass
class ChannelList:
    data: list[Channel]

    @staticmethod
    def from_domain(channel_list: list[Channel]) -> "ChannelList":
        return ChannelList(
            data=[
                Channel(channel_id=channel.channel_id, book_name=channel.book_name)
                for channel in channel_list
            ],
        )

    @staticmethod
    def to_string(channels: "ChannelList") -> str:
        channel_list = "".join(
            [f"({book.book_name})[#{book.channel_id}]\n" for book in channels.data]
        )
        return f"List of channels: {channel_list}"


@dataclass
class Book:
    isbn: str
    title: str
    author: str
    page_count: int
    state: State
    type: Type
    chapter_number: int = 0
    current_chapter: int = 0
    current_page: int = 0
    channel_id: str = os.getenv("DEFAULT_SLACK_CHANNEL", "123456")

    @staticmethod
    def to_json(book: "Book") -> dict:
        return {
            "isbn": book.isbn,
            "title": book.title,
            "author": book.author,
            "page_count": book.page_count,
            "state": book.state.value,
            "type": book.type.value,
            "chapter_number": book.chapter_number,
            "current_chapter": book.current_chapter,
            "current_page": book.current_page,
            "channel_id": book.channel_id,
        }

    @staticmethod
    def from_json(dict: dict) -> "Book":
        return Book(
            isbn=dict.get("isbn", "Unknown"),
            title=dict.get("title", "Unknown"),
            author=dict.get("author", "Unknown"),
            page_count=dict.get("page_count", 0),
            state=State(dict.get("state")),
            type=Type(dict.get("type")),
            chapter_number=dict.get("chapter_number", 0),
            current_chapter=dict.get("current_chapter", 0),
            current_page=dict.get("current_page", 0),
            channel_id=dict.get("channel_id", ""),
        )
