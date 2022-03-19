from typing import TypedDict


class CSVTask(TypedDict):
    id: int
    data: str


class CSVTaskResponse(TypedDict):
    data: str
