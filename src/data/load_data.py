"""Utilities to load raw transaction datasets for Phase 1 (Data + EDA)."""

from pathlib import Path
from typing import Iterable

import pandas as pd

from src.utils.logger import get_logger

logger = get_logger(__name__)

RAW_DATA_DIR = Path("data/raw")
DEFAULT_FILE_NAME = "transactions.csv"
DEFAULT_CANDIDATE_FILES = (
    "transactions.csv",
    "creditcard.csv",
    "train_transaction.csv",
)
DEFAULT_REQUIRED_COLUMN_GROUPS = (
    ("Amount", "Time"),
    ("TransactionAmt", "TransactionDT"),
)
TARGET_CANDIDATES = ("isFraud", "Class", "fraud", "target")


def _resolve_raw_file(file_name: str | None = None) -> Path:
    """Resolve which CSV should be loaded from data/raw."""
    if file_name:
        file_path = RAW_DATA_DIR / file_name
        if not file_path.exists():
            raise FileNotFoundError(
                f"Raw data file not found: '{file_path}'. "
                "Place your CSV inside data/raw/."
            )
        return file_path

    for candidate in DEFAULT_CANDIDATE_FILES:
        candidate_path = RAW_DATA_DIR / candidate
        if candidate_path.exists():
            return candidate_path

    available_csv = sorted(path.name for path in RAW_DATA_DIR.glob("*.csv"))
    raise FileNotFoundError(
        "No dataset CSV found in data/raw/. "
        f"Expected one of {DEFAULT_CANDIDATE_FILES} or pass file_name explicitly. "
        f"Available CSV files: {available_csv if available_csv else 'none'}."
    )


def _validate_columns(
    df: pd.DataFrame,
    required_columns: Iterable[str] | None = None,
) -> None:
    """Validate key dataset columns for Phase 1 checks."""
    if df.empty:
        raise ValueError("Dataset is empty. Verify the raw CSV content.")

    if required_columns:
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        return

    has_target = any(col in df.columns for col in TARGET_CANDIDATES)
    if not has_target:
        raise ValueError(
            "Target column not found. Expected one of: "
            f"{list(TARGET_CANDIDATES)}."
        )

    has_minimum_structure = any(
        all(column in df.columns for column in group)
        for group in DEFAULT_REQUIRED_COLUMN_GROUPS
    )
    if not has_minimum_structure:
        raise ValueError(
            "Dataset does not match expected fraud schema. Expected one of these "
            "column groups: "
            f"{[list(group) for group in DEFAULT_REQUIRED_COLUMN_GROUPS]}."
        )


def load_raw_data(
    file_name: str | None = None,
    required_columns: Iterable[str] | None = None,
) -> pd.DataFrame:
    """
    Load raw fraud data from data/raw and validate key columns.

    Args:
        file_name: CSV name inside data/raw/. If None, uses known defaults.
        required_columns: Optional exact required columns to enforce.

    Returns:
        Pandas DataFrame with raw transactions.
    """
    file_path = _resolve_raw_file(file_name=file_name)
    logger.info(f"Loading raw data from {file_path}")
    df = pd.read_csv(file_path)
    _validate_columns(df, required_columns=required_columns)
    logger.info(f"Loaded raw data: {df.shape[0]:,} rows x {df.shape[1]} columns")
    return df


def load_data(file_name: str | None = None) -> pd.DataFrame:
    """Backward-compatible alias for existing imports."""
    return load_raw_data(file_name=file_name)


if __name__ == "__main__":
    dataset = load_raw_data()
    print(f"Raw dataset shape: {dataset.shape}")
    print(f"Columns ({len(dataset.columns)}): {list(dataset.columns)}")