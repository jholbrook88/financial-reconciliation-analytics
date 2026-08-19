"""Project settings kept in one place for easy review and modification."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ReconciliationConfig:
    project_dir: Path
    source_dir: Path
    bank_statement_path: Path
    output_dir: Path
    statement_start: str = "2026-06-01"
    statement_end: str = "2026-06-30"
    ledger_lookback_days: int = 7
    ledger_lookahead_days: int = 0
    cash_account_id: int = 2
    timing_window_days: int = 7
    amount_tolerance: float = 0.99
    description_threshold: float = 0.45


def default_config() -> ReconciliationConfig:
    project_dir = Path(__file__).resolve().parents[1]
    portfolio_dir = project_dir.parent
    return ReconciliationConfig(
        project_dir=project_dir,
        source_dir=portfolio_dir / "CharlesRiver_csv",
        bank_statement_path=project_dir
        / "data"
        / "sample"
        / "charles_river_simulated_bank_statement_june_2026.xlsx",
        output_dir=project_dir / "output",
    )
