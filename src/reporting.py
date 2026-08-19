"""Write reconciliation results and control totals to auditable files."""

import json
from pathlib import Path

import pandas as pd


def build_summary(
    bank: pd.DataFrame,
    ledger: pd.DataFrame,
    matched: pd.DataFrame,
    bank_exceptions: pd.DataFrame,
    ledger_exceptions: pd.DataFrame,
) -> dict:
    matched_bank_amount = matched["BankAmount"].sum() if not matched.empty else 0.0
    return {
        "bank_transaction_count": int(len(bank)),
        "ledger_transaction_count": int(len(ledger)),
        "matched_count": int(len(matched)),
        "bank_exception_count": int(len(bank_exceptions)),
        "ledger_exception_count": int(len(ledger_exceptions)),
        "match_rate_bank": round(len(matched) / len(bank), 4) if len(bank) else 0.0,
        "bank_net_activity": round(float(bank["Net Amount"].sum()), 2),
        "ledger_net_activity": round(float(ledger["Amount"].sum()), 2),
        "matched_bank_amount": round(float(matched_bank_amount), 2),
        "bank_exception_net_amount": round(
            float(bank_exceptions["Net Amount"].sum()), 2
        ),
        "ledger_exception_net_amount": round(
            float(ledger_exceptions["Amount"].sum()), 2
        ),
    }


def write_outputs(
    output_dir: Path,
    ledger: pd.DataFrame,
    matched: pd.DataFrame,
    bank_exceptions: pd.DataFrame,
    ledger_exceptions: pd.DataFrame,
    summary: dict,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    ledger.to_csv(output_dir / "cash_ledger_extract.csv", index=False)
    matched.to_csv(output_dir / "matched_transactions.csv", index=False)
    bank_exceptions.to_csv(output_dir / "bank_exceptions.csv", index=False)
    ledger_exceptions.to_csv(output_dir / "ledger_exceptions.csv", index=False)
    (output_dir / "reconciliation_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

