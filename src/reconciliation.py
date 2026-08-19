"""One-to-one transaction matching rules for bank-to-ledger reconciliation."""

import re
from difflib import SequenceMatcher

import pandas as pd

from .config import ReconciliationConfig


def normalize_text(value: object) -> str:
    text = "" if pd.isna(value) else str(value).upper()
    return re.sub(r"[^A-Z0-9]+", "", text)


def description_similarity(left: object, right: object) -> float:
    return SequenceMatcher(None, normalize_text(left), normalize_text(right)).ratio()


def _candidate(
    bank_row: pd.Series,
    ledger_row: pd.Series,
    rule: str,
    config: ReconciliationConfig,
) -> tuple[bool, float]:
    amount_difference = abs(float(bank_row["Net Amount"]) - float(ledger_row["Amount"]))
    date_difference = abs((bank_row["Date"] - ledger_row["PostingDate"]).days)
    same_reference = normalize_text(bank_row["Reference"]) == normalize_text(
        ledger_row["Reference"]
    )

    if rule == "reference_exact":
        return same_reference and amount_difference <= 0.005, 1.0
    if rule == "amount_timing":
        return (
            amount_difference <= 0.005
            and date_difference <= config.timing_window_days,
            1.0 - date_difference / (config.timing_window_days + 1),
        )
    if rule == "tolerance_description":
        similarity = description_similarity(
            bank_row["Description"], ledger_row["Description"]
        )
        return (
            amount_difference <= config.amount_tolerance
            and date_difference <= config.timing_window_days
            and similarity >= config.description_threshold,
            similarity,
        )
    raise ValueError(f"Unknown reconciliation rule: {rule}")


def reconcile(
    bank: pd.DataFrame, ledger: pd.DataFrame, config: ReconciliationConfig
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ledger_reference_index: dict[str, list[int]] = {}
    ledger_amount_index: dict[int, list[int]] = {}
    for ledger_index, ledger_row in ledger.iterrows():
        reference_key = normalize_text(ledger_row["Reference"])
        amount_key = round(float(ledger_row["Amount"]) * 100)
        ledger_reference_index.setdefault(reference_key, []).append(ledger_index)
        ledger_amount_index.setdefault(amount_key, []).append(ledger_index)

    available_ledger = set(ledger.index)
    matches: list[dict] = []
    matched_bank: set[int] = set()

    for rule in ("reference_exact", "amount_timing", "tolerance_description"):
        for bank_index, bank_row in bank.iterrows():
            if bank_index in matched_bank:
                continue

            bank_amount_key = round(float(bank_row["Net Amount"]) * 100)
            if rule == "reference_exact":
                candidate_pool = ledger_reference_index.get(
                    normalize_text(bank_row["Reference"]), []
                )
            elif rule == "amount_timing":
                candidate_pool = ledger_amount_index.get(bank_amount_key, [])
            else:
                tolerance_cents = round(config.amount_tolerance * 100)
                candidate_pool = [
                    ledger_index
                    for amount_key in range(
                        bank_amount_key - tolerance_cents,
                        bank_amount_key + tolerance_cents + 1,
                    )
                    for ledger_index in ledger_amount_index.get(amount_key, [])
                ]

            candidates = []
            for ledger_index in candidate_pool:
                if ledger_index not in available_ledger:
                    continue
                ledger_row = ledger.loc[ledger_index]
                is_match, score = _candidate(bank_row, ledger_row, rule, config)
                if is_match:
                    date_difference = abs(
                        (bank_row["Date"] - ledger_row["PostingDate"]).days
                    )
                    amount_difference = abs(
                        float(bank_row["Net Amount"]) - float(ledger_row["Amount"])
                    )
                    candidates.append(
                        (date_difference, amount_difference, -score, ledger_index, score)
                    )

            if not candidates:
                continue

            _, amount_difference, _, ledger_index, score = min(candidates)
            ledger_row = ledger.loc[ledger_index]
            matches.append(
                {
                    "BankRowID": bank_row["BankRowID"],
                    "GLEntryID": ledger_row["GLEntryID"],
                    "MatchRule": rule,
                    "BankDate": bank_row["Date"],
                    "PostingDate": ledger_row["PostingDate"],
                    "BankReference": bank_row["Reference"],
                    "LedgerReference": ledger_row["Reference"],
                    "BankAmount": bank_row["Net Amount"],
                    "LedgerAmount": ledger_row["Amount"],
                    "AmountDifference": round(amount_difference, 2),
                    "DaysDifference": abs(
                        (bank_row["Date"] - ledger_row["PostingDate"]).days
                    ),
                    "DescriptionScore": round(score, 3),
                }
            )
            matched_bank.add(bank_index)
            available_ledger.remove(ledger_index)

    matched = pd.DataFrame(matches)
    bank_exceptions = bank.loc[~bank.index.isin(matched_bank)].copy()
    ledger_exceptions = ledger.loc[sorted(available_ledger)].copy()
    return matched, bank_exceptions, ledger_exceptions
