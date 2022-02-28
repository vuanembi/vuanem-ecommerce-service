from typing import TypedDict, Optional
from dataclasses import dataclass

from netsuite.query.saved_search import saved_search

CUSTBODY_JOURNAL_TYPE2 = 6
CUSTBODY_CASH_FLOW_CODE = 4100

BANK_IN_TRANSIT_DR_LOCATION = 28


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


@dataclass
class BankInTransitOptions:
    name: str
    saved_search: str
    account_filter: str
    dr_account: int
    cr_account: int


BankInTransitWarehouse = BankInTransitOptions(
    "Warehouse",
    saved_search.SavedSearch.BankInTransitWarehouse.value,
    "113343",
    754,
    1232,
)
BankInTransitOnline = BankInTransitOptions(
    "Online",
    saved_search.SavedSearch.BankInTransitWarehouse.value,
    "113361",
    1154,
    1173,
)
