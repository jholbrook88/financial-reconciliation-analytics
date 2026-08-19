# Financial Reconciliation Analytics

This project uses Python to compare a bank statement with general-ledger cash
activity. It matches transactions and separates anything that still needs to
be reviewed.

I built it to practice combining accounting knowledge with Python and data
analysis. The data comes from a fictional company, so no real customer or
bank information is used.

## What it does

The program:

1. Reads a simulated June 2026 bank statement.
2. Pulls cash transactions from the Charles River general ledger.
3. Adds useful references and descriptions from related accounting tables.
4. Matches each bank transaction to no more than one ledger transaction.
5. Saves the matches and exceptions as CSV files.

## Results

| Metric | Result |
|---|---:|
| Bank transactions | 2,039 |
| Ledger transactions reviewed | 2,320 |
| Matched transactions | 2,035 |
| Bank exceptions | 4 |
| Ledger exceptions | 285 |
| Bank match rate | 99.8% |

The four bank exceptions were test cases added to the simulated statement:

- a monthly bank fee
- a returned customer ACH payment
- a wire fee
- interest income

The ledger exceptions are transactions that were recorded in the ledger but
did not appear on the June bank statement. Some may be normal timing items,
such as outstanding checks or deposits in transit. They still require review.

More detail is available in [reports/RESULTS.md](reports/RESULTS.md).

## How matching works

The program tries three rules in order:

1. Same reference and amount
2. Same amount within seven days
3. Similar description, date within seven days, and amount within $0.99

Once a transaction is matched, it cannot be used again. This helps prevent a
duplicate transaction from being treated as a valid match.

## Project layout

```text
financial-reconciliation-analytics/
├── data/sample/        Simulated bank statement
├── output/             Files created when the program runs
├── reports/            Summary of the results
├── src/                Python code
├── tests/              Automated tests
└── requirements.txt    Python packages
```

The main Python files are:

- `config.py` — dates, file locations, and matching settings
- `data_loading.py` — loads and checks the bank statement
- `ledger_extract.py` — builds the cash-ledger file
- `reconciliation.py` — contains the matching rules
- `reporting.py` — saves the results
- `main.py` — runs the full process

## Data setup

This project uses the
[Charles River Accounting Dataset](https://charlesriver.accountinganalyticshub.com/).
Download the CSV package from its
[download page](https://charlesriver.accountinganalyticshub.com/docs/downloads).

By default, the folders should look like this:

```text
Portfolio/
├── CharlesRiver_csv/
└── financial-reconciliation-analytics/
```

The simulated bank statement is already included in `data/sample/`.

## Running the project

I use PyCharm, but the commands work in any terminal with Python 3.11 or newer.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m src.main
```

If your Charles River folder is somewhere else:

```powershell
python -m src.main --source-dir "C:\path\to\CharlesRiver_csv"
```

The finished files are saved in `output/`:

- `cash_ledger_extract.csv`
- `matched_transactions.csv`
- `bank_exceptions.csv`
- `ledger_exceptions.csv`
- `reconciliation_summary.json`

## Tests

```powershell
python -m unittest discover -s tests -v
```

GitHub Actions also runs the tests automatically.

## Limitations

This is a portfolio project built with synthetic data. The matching results
still need accounting review, especially the ledger exceptions. The project
does not represent a real audit or a production accounting system.

## Author

Jason Holbrook  
[LinkedIn](https://www.linkedin.com/in/jholbrook88) ·
[GitHub](https://github.com/jholbrook88)
