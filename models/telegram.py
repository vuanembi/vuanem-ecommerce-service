from typing import TypedDict, Any


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


Payload = dict[str, Any]

class CalbackData(TypedDict):
    t: str
    a: int
    v: str
