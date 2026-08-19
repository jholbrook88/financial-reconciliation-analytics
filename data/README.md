# Data setup

The project separates the accounting source data from the code repository so
the repository remains small and the original dataset is not duplicated.

## Required accounting tables

Download the CSV package from the Charles River Accounting Dataset:

https://charlesriver.accountinganalyticshub.com/docs/downloads

Extract the package so the default local layout is:

```text
Portfolio/
├── CharlesRiver_csv/
│   ├── GLEntry.csv
│   ├── Account.csv
│   ├── CashReceipt.csv
│   └── ...
└── financial-reconciliation-analytics/
```

Alternatively, supply any location at runtime:

```powershell
python -m src.main --source-dir "C:\path\to\CharlesRiver_csv"
```

## Included sample statement

`sample/charles_river_simulated_bank_statement_june_2026.xlsx` is an adapted,
synthetic bank-side view created from cash-related events in the Charles River
dataset. Four bank-originated exception scenarios were inserted for testing:

- monthly account-maintenance fee
- returned customer ACH
- wire-processing fee
- monthly interest credit

The statement and any other dataset adaptations are distributed under CC
BY-SA 4.0. See `DATA_LICENSE.md` in the repository root.

