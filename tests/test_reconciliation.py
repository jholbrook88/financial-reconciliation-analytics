from pathlib import Path
import unittest

import pandas as pd

from src.config import ReconciliationConfig
from src.reconciliation import normalize_text, reconcile


class ReconciliationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = ReconciliationConfig(
        project_dir=Path("."),
        source_dir=Path("."),
        bank_statement_path=Path("statement.xlsx"),
        output_dir=Path("output"),
    )

    def test_normalize_text_removes_formatting(self) -> None:
        self.assertEqual(normalize_text(" INV-123 / abc "), "INV123ABC")

    def test_reference_match_is_one_to_one(self) -> None:
        bank = pd.DataFrame(
        [
            {
                "BankRowID": 1,
                "Date": pd.Timestamp("2026-06-05"),
                "Reference": "CHK-100",
                "Description": "Supplier payment",
                "Net Amount": -250.0,
            },
            {
                "BankRowID": 2,
                "Date": pd.Timestamp("2026-06-05"),
                "Reference": "CHK-100",
                "Description": "Duplicate bank row",
                "Net Amount": -250.0,
            },
        ]
    )
        ledger = pd.DataFrame(
        [
            {
                "GLEntryID": 10,
                "PostingDate": pd.Timestamp("2026-06-03"),
                "Reference": "CHK100",
                "Description": "Supplier payment",
                "Amount": -250.0,
            }
        ]
    )

        matched, bank_exceptions, ledger_exceptions = reconcile(
            bank, ledger, self.config
        )

        self.assertEqual(len(matched), 1)
        self.assertEqual(len(bank_exceptions), 1)
        self.assertTrue(ledger_exceptions.empty)


    def test_tolerance_match_uses_description_and_date(self) -> None:
        bank = pd.DataFrame(
        [
            {
                "BankRowID": 1,
                "Date": pd.Timestamp("2026-06-10"),
                "Reference": "BANK-1",
                "Description": "ACH payment Acme Supply",
                "Net Amount": -100.45,
            }
        ]
    )
        ledger = pd.DataFrame(
        [
            {
                "GLEntryID": 11,
                "PostingDate": pd.Timestamp("2026-06-08"),
                "Reference": "GL-9",
                "Description": "Acme Supply ACH payment",
                "Amount": -100.0,
            }
        ]
    )

        matched, bank_exceptions, ledger_exceptions = reconcile(
            bank, ledger, self.config
        )

        self.assertEqual(matched.iloc[0]["MatchRule"], "tolerance_description")
        self.assertTrue(bank_exceptions.empty)
        self.assertTrue(ledger_exceptions.empty)


if __name__ == "__main__":
    unittest.main()
