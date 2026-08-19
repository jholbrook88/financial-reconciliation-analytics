"""Functions for loading and validating the bank statement and source tables."""

from pathlib import Path

import pandas as pd


BANK_COLUMNS = {
    "Date",
    "Reference",
    "Description",
    "Transaction Type",
    "Net Amount",
}


def require_columns(frame: pd.DataFrame, required: set[str], source_name: str) -> None:
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"{source_name} is missing required columns: {sorted(missing)}")


def load_csv(source_dir: Path, table_name: str) -> pd.DataFrame:
    path = source_dir / f"{table_name}.csv"
    if not path.exists():
        raise FileNotFoundError(f"Required source table was not found: {path}")
    return pd.read_csv(path)


def load_bank_statement(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Bank statement was not found: {path}")

    bank = pd.read_excel(path, sheet_name="Bank Statement", header=10)
    require_columns(bank, BANK_COLUMNS, "Bank statement")
    bank = bank.loc[bank["Date"].notna()].copy()
    bank["Date"] = pd.to_datetime(bank["Date"], errors="raise")
    bank["Net Amount"] = pd.to_numeric(bank["Net Amount"], errors="raise").round(2)
    bank["Reference"] = bank["Reference"].fillna("").astype(str).str.strip()
    bank["Description"] = bank["Description"].fillna("").astype(str).str.strip()
    bank = bank.reset_index(drop=True)
    bank.insert(0, "BankRowID", range(1, len(bank) + 1))
    return bank

