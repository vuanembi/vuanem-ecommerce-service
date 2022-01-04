from typing import TypedDict, Any, Callable
from dataclasses import dataclass
import os

# ---------------------------------- Message --------------------------------- #


@dataclass(frozen=True)
class Channel:
    ecom: str
    chat_id: str


TIKI_CHANNEL = Channel(
    "Tiki",
    "-1001685563275" if os.getenv("PYTHON_ENV") == "prod" else "-645664226",
)
LAZADA_CHANNEL = Channel(
    "LAZADA",
    "-661578343" if os.getenv("PYTHON_ENV") == "prod" else "-645664226",
)


Payload = dict[str, Any]
PayloadBuilder = Callable[[Payload], Payload]


class CalbackData(TypedDict):
    t: str
    a: int
    v: str


# --------------------------------- Callback --------------------------------- #


class Chat(TypedDict):
    id: int


class Message(TypedDict):
    chat: Chat


class CallbackQuery(TypedDict):
    id: str
    message: Message
    data: str


class Update(TypedDict):
    update_id: str
    callback_query: CallbackQuery
