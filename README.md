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

## Checking the matching rules

```powershell
python -m unittest discover -s tests -v
```

## What I learned

This project helped me connect my accounting education and banking experience
with Python. I practiced cleaning financial data, matching transactions without
using the same ledger entry twice, and separating items that need review. I also
learned that a high match rate does not mean the reconciliation is finished.

## Limitations

This is a learning project using fictional data, and most transactions match by
reference number. Real data would be messier, and the unmatched items would still
need to be reviewed by a person.

## Author

Jason Holbrook  
[LinkedIn](https://www.linkedin.com/in/jholbrook88) ·
[GitHub](https://github.com/jholbrook88)
