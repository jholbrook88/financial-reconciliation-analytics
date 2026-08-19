"""Command-line entry point for the reconciliation pipeline."""

import argparse
import json
from dataclasses import replace
from pathlib import Path

from .config import default_config
from .data_loading import load_bank_statement
from .ledger_extract import build_cash_ledger
from .reconciliation import reconcile
from .reporting import build_summary, write_outputs


def parse_args() -> argparse.Namespace:
    defaults = default_config()
    parser = argparse.ArgumentParser(
        description="Reconcile a simulated bank statement to Charles River cash GL activity."
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=defaults.source_dir,
        help="Folder containing the extracted Charles River CSV tables.",
    )
    parser.add_argument(
        "--bank-statement",
        type=Path,
        default=defaults.bank_statement_path,
        help="Path to the simulated bank-statement workbook.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=defaults.output_dir,
        help="Folder for generated reconciliation outputs.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = default_config()
    config = replace(
        config,
        source_dir=args.source_dir.resolve(),
        bank_statement_path=args.bank_statement.resolve(),
        output_dir=args.output_dir.resolve(),
    )
    bank = load_bank_statement(config.bank_statement_path)
    ledger = build_cash_ledger(config)
    matched, bank_exceptions, ledger_exceptions = reconcile(bank, ledger, config)
    summary = build_summary(
        bank, ledger, matched, bank_exceptions, ledger_exceptions
    )
    write_outputs(
        config.output_dir,
        ledger,
        matched,
        bank_exceptions,
        ledger_exceptions,
        summary,
    )
    print(json.dumps(summary, indent=2))
    print(f"\nOutputs written to: {config.output_dir}")


if __name__ == "__main__":
    main()
