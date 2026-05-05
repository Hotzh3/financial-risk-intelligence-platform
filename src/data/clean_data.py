"""Data cleaning pipeline for Phase 1 (Data + EDA)."""

from pathlib import Path

import pandas as pd

from src.data.load_data import load_raw_data
from src.utils.logger import get_logger

logger = get_logger(__name__)

PROCESSED_OUTPUT_PATH = Path("data/processed/transactions_clean.csv")


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Drop duplicate rows and log how many were removed."""
    before = len(df)
    cleaned = df.drop_duplicates().copy()
    removed = before - len(cleaned)
    logger.info(f"Removed duplicates: {removed}")
    return cleaned


def convert_numeric_types(df: pd.DataFrame) -> pd.DataFrame:
    """Convert object columns to numeric when conversion is possible."""
    converted = df.copy()
    object_columns = converted.select_dtypes(include=["object"]).columns
    for column in object_columns:
        numeric_version = pd.to_numeric(converted[column], errors="coerce")
        original_non_null = converted[column].notna().sum()
        converted_non_null = numeric_version.notna().sum()
        if original_non_null > 0 and (converted_non_null / original_non_null) >= 0.9:
            converted[column] = numeric_version
    return converted


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing values with simple, interview-friendly rules."""
    cleaned = df.copy()
    numeric_columns = cleaned.select_dtypes(include=["number"]).columns
    categorical_columns = cleaned.select_dtypes(exclude=["number"]).columns

    for column in numeric_columns:
        if cleaned[column].isna().any():
            cleaned[column] = cleaned[column].fillna(cleaned[column].median())

    for column in categorical_columns:
        if cleaned[column].isna().any():
            cleaned[column] = cleaned[column].fillna("Unknown")

    return cleaned


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Run the full data cleaning pipeline."""
    cleaned = remove_duplicates(df)
    cleaned = convert_numeric_types(cleaned)
    cleaned = handle_missing_values(cleaned)
    return cleaned


def save_processed_data(df: pd.DataFrame, output_path: Path = PROCESSED_OUTPUT_PATH) -> Path:
    """Save cleaned data into data/processed and return saved path."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info(f"Saved cleaned dataset to {output_path}")
    return output_path


if __name__ == "__main__":
    raw_df = load_raw_data()
    clean_df = clean_data(raw_df)
    saved_path = save_processed_data(clean_df)

    print(f"Raw shape: {raw_df.shape}")
    print(f"Clean shape: {clean_df.shape}")
    print(f"Saved cleaned dataset: {saved_path}")