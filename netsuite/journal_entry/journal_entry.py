from typing import TypedDict

CUSTBODY_JOURNAL_TYPE2 = 6
CUSTBODY_CASH_FLOW_CODE = 4100


class Line(TypedDict):
    line_type: str
    account: int
    entity: int
    location: int
    amount: int


class JournalEntryDraft(TypedDict):
    subsidiary: int
    custbody_ref_transaction: int
    memo: str
    trandate: str
    lines: list[Line]


class JournalEntry(JournalEntryDraft):
    custbody_journal_type2: int
    custbody_cash_flow_code: int
