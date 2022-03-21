from typing import Callable, TypedDict, Optional
from dataclasses import dataclass

from netsuite.query.saved_search import saved_search

CUSTBODY_JOURNAL_TYPE2 = 6
CUSTBODY_CASH_FLOW_CODE = 4100

BANK_IN_TRANSIT_LOCATION = 28

BANK_IN_TRANSIT_MIDDLE_ACCOUNT = 221


class _Line(TypedDict):
    line_type: str
    account: int
    entity: Optional[int]
    amount: int


class Line(_Line, total=False):
    location: int
    subsidiary: int


class JournalEntryDraft(TypedDict):
    custbody_ref_transaction: Optional[int]
    subsidiary: int
    memo: str
    trandate: str
    lines: list[Line]


class JournalEntry(JournalEntryDraft):
    custbody_journal_type2: int
    custbody_cash_flow_code: int


def build_bank_in_transit_lines(dr_account: int, cr_account: int):
    def _build(entries_group: tuple[str, list[dict]]) -> list[Line]:
        _, entries = entries_group
        return [
            {
                "line_type": "debit",
                "account": dr_account,
                "entity": None,
                "location": BANK_IN_TRANSIT_LOCATION,
                "amount": int(sum([float(entry["amount"]) for entry in entries])),
            },
            *[  # type: ignore
                {
                    "line_type": "credit",
                    "account": cr_account,
                    "entity": int(entry["internalid"]),
                    "location": int(entry["custbody_in_charge_location"]),
                    "amount": int(float(entry["amount"])),
                }
                for entry in entries
            ],
        ]

    return _build


def build_bank_in_transit_lines_with_payment_method(
    entries_group: tuple[str, list[dict]]
) -> list[Line]:
    group, entries = entries_group
    subsidiary_id, custbody_deposit_payment_method = [int(i) for i in group.split("-")]
    dr_account = 1154 if int(custbody_deposit_payment_method) == 13 else 1218
    cr_account = 1052 if int(custbody_deposit_payment_method) == 13 else 1233
    if subsidiary_id == 1:
        return [
            {
                "line_type": "debit",
                "account": dr_account,
                "entity": None,
                "location": BANK_IN_TRANSIT_LOCATION,
                "amount": int(sum([float(entry["amount"]) for entry in entries])),
            },
            *[  # type: ignore
                {
                    "line_type": "credit",
                    "account": cr_account,
                    "entity": int(entry["internalid"]),
                    "location": int(entry["custbody_in_charge_location"]),
                    "amount": int(float(entry["amount"])),
                }
                for entry in entries
            ],
        ]
    else:
        return [
            {
                "line_type": "debit",
                "account": BANK_IN_TRANSIT_MIDDLE_ACCOUNT,
                "entity": None,
                "subsidiary": subsidiary_id,
                "amount": int(sum([float(entry["amount"]) for entry in entries])),
            },
            *[  # type: ignore
                {
                    "line_type": "credit",
                    "account": cr_account,
                    "entity": int(entry["internalid"]),
                    "location": int(entry["custbody_in_charge_location"]),
                    "amount": int(float(entry["amount"])),
                }
                for entry in entries
            ],
            {
                "line_type": "debit",
                "account": dr_account,
                "entity": None,
                "location": BANK_IN_TRANSIT_LOCATION,
                "amount": int(sum([float(entry["amount"]) for entry in entries])),
            },
            {
                "line_type": "credit",
                "account": BANK_IN_TRANSIT_MIDDLE_ACCOUNT,
                "entity": None,
                "location": BANK_IN_TRANSIT_LOCATION,
                "amount": int(sum([float(entry["amount"]) for entry in entries])),
            },
        ]


@dataclass
class BankInTransitOptions:
    name: str
    saved_search: str
    account_filter: list[str]
    group_key_fn: Callable[[dict], Optional[str]]
    build_fn: Callable[[tuple[str, list[dict]]], list[Line]]


BankInTransitWarehouse = BankInTransitOptions(
    "Warehouse",
    saved_search.SavedSearch.BankInTransitWarehouse.value,
    ["113343"],
    lambda _: None,
    build_bank_in_transit_lines(754, 1232),
)
BankInTransitOnline = BankInTransitOptions(
    "Online",
    saved_search.SavedSearch.BankInTransitOnline.value,
    ["113361"],
    lambda _: None,
    build_bank_in_transit_lines(1154, 1173),
)
BankInTransitVNPay = BankInTransitOptions(
    "VNPay",
    saved_search.SavedSearch.BankInTransitVNPay.value,
    ["113344", "113360"],
    lambda e: e["subsidiary_id"],
    build_bank_in_transit_lines_with_payment_method,
)
