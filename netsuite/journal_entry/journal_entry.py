from typing import TypedDict, Optional

CUSTBODY_JOURNAL_TYPE2 = 6
CUSTBODY_CASH_FLOW_CODE = 4100

BANK_IN_TRANSIT_DR_LOCATION = 28
BANK_IN_TRANSIT_DR_ACCOUNT = 754

BANK_IN_TRANSIT_CR_ACCOUNT = 1232


class Line(TypedDict):
    line_type: str
    account: int
    entity: Optional[int]
    location: int
    amount: int


class JournalEntryDraft(TypedDict):
    custbody_ref_transaction: Optional[int]
    subsidiary: int
    memo: str
    trandate: str
    lines: list[Line]


class JournalEntry(JournalEntryDraft):
    custbody_journal_type2: int
    custbody_cash_flow_code: int
