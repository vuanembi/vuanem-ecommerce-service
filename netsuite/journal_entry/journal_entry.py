from typing import Callable, TypedDict, Optional
from dataclasses import dataclass

from netsuite.location import location

CUSTBODY_JOURNAL_TYPE2 = 6
CUSTBODY_CASH_FLOW_CODE = 4100

BANK_IN_TRANSIT_LOCATION = 28

BANK_IN_TRANSIT_MIDDLE_ACCOUNT = 221


class _Line(TypedDict):
    line_type: str
    account: int
    entity: Optional[int]
    amount: int
    location: int


class Line(_Line, total=False):
    linesubsidiary: int


class _JournalEntryDraft(TypedDict):
    subsidiary: int
    memo: str
    trandate: str
    lines: list[Line]


class JournalEntryDraft(_JournalEntryDraft, total=False):
    tosubsidiary: int
    _intercompany: bool


class JournalEntry(JournalEntryDraft):
    custbody_journal_type2: int
    custbody_cash_flow_code: int


def build_bank_in_transit_journal_entry(dr_account: int, cr_account: int):
    def _build(entries_group: tuple[str, list[dict]]) -> list[Line]:
        _, entries = entries_group
        return {
            "subsidiary": location.SUBSIDIARY,
            "lines": [
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
                        "entity": int(entry["entity"]),
                        "location": int(entry["custbody_in_charge_location"]),
                        "amount": int(float(entry["amount"])),
                    }
                    for entry in entries
                ],
            ],
        }

    return _build


def build_bank_in_transit_journal_entry_with_payment_method(
    entries_group: tuple[str, list[dict]]
) -> list[Line]:
    group, entries = entries_group
    subsidiary, custbody_in_charge_location, custbody_payment_method = [
        int(i) for i in group
    ]
    dr_account = 1154 if custbody_payment_method == 13 else 1218
    cr_account = 1052 if custbody_payment_method == 13 else 1233
    if subsidiary == 1:
        return {
            "subsidiary": location.SUBSIDIARY,
            "lines": [
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
                        "entity": int(entry["entity"]),
                        "location": int(entry["custbody_in_charge_location"]),
                        "amount": int(float(entry["amount"])),
                    }
                    for entry in entries
                ],
            ],
        }
    else:
        return {
            "subsidiary": subsidiary,
            "tosubsidiary": location.SUBSIDIARY,
            "lines": [
                {
                    "line_type": "debit",
                    "account": BANK_IN_TRANSIT_MIDDLE_ACCOUNT,
                    "entity": None,
                    "linesubsidiary": subsidiary,
                    "location": custbody_in_charge_location,
                    "amount": int(sum([float(entry["amount"]) for entry in entries])),
                },
                *[  # type: ignore
                    {
                        "line_type": "credit",
                        "account": cr_account,
                        "entity": int(entry["entity"]),
                        "location": int(entry["custbody_in_charge_location"]),
                        "linesubsidiary": subsidiary,
                        "amount": int(float(entry["amount"])),
                    }
                    for entry in entries
                ],
                {
                    "line_type": "debit",
                    "account": dr_account,
                    "entity": None,
                    "location": BANK_IN_TRANSIT_LOCATION,
                    "linesubsidiary": location.SUBSIDIARY,
                    "amount": int(sum([float(entry["amount"]) for entry in entries])),
                },
                {
                    "line_type": "credit",
                    "account": BANK_IN_TRANSIT_MIDDLE_ACCOUNT,
                    "entity": None,
                    "location": BANK_IN_TRANSIT_LOCATION,
                    "linesubsidiary": location.SUBSIDIARY,
                    "amount": int(sum([float(entry["amount"]) for entry in entries])),
                },
            ],
            "_intercompany": True,
        }


@dataclass
class BankInTransitOptions:
    name: str
    account_filter: list[str]
    group_key_fn: Callable[[dict], Optional[tuple]]
    build_fn: Callable[[tuple[str, list[dict]]], list[Line]]


BankInTransitWarehouse = BankInTransitOptions(
    "Warehouse",
    ["113343"],
    lambda e: (e["subsidiary"]),
    build_bank_in_transit_journal_entry(754, 1232),
)

BankInTransitOnline = BankInTransitOptions(
    "Online",
    ["113361"],
    lambda e: (e["subsidiary"]),
    build_bank_in_transit_journal_entry(1154, 1173),
)

BankInTransitVNPay = BankInTransitOptions(
    "VNPay",
    ["113344", "113360"],
    lambda e: (
        e["subsidiary"],
        e["custbody_in_charge_location"],
        e["custbody_payment_method"],
    ),
    build_bank_in_transit_journal_entry_with_payment_method,
)
