"""
Data cleaning pipeline for the Financial Risk Intelligence Platform.
Handles missing values, data types, and basic feature preparation.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from src.utils.logger import get_logger
from src.data.load_data import load_data

logger = get_logger(__name__)


def get_missing_report(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate missing values report.

    Args:
        df: Input DataFrame

    Returns:
        DataFrame with missing value statistics per column
    """
    missing = df.isnull().sum()
    missing_pct = (missing / len(df)) * 100
    report = pd.DataFrame({
        "missing_count": missing,
        "missing_pct": missing_pct
    })
    report = report[report["missing_count"] > 0].sort_values(
        "missing_pct", ascending=False
    )
    return report


def drop_high_missing_columns(
    df: pd.DataFrame,
    threshold: float = 0.5
) -> pd.DataFrame:
    """
    Drop columns with more than threshold% missing values.

    Args:
        df: Input DataFrame
        threshold: Maximum allowed missing ratio (default 50%)

    Returns:
        DataFrame with high-missing columns removed
    """
    missing_pct = df.isnull().mean()
    cols_to_drop = missing_pct[missing_pct > threshold].index.tolist()
    logger.info(f"Dropping {len(cols_to_drop)} columns with >{threshold*100:.0f}% missing values")
    return df.drop(columns=cols_to_drop)


def fill_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill missing values by data type.
    - Numeric columns: fill with median
    - Categorical columns: fill with 'Unknown'

    Args:
        df: Input DataFrame

    Returns:
        DataFrame with no missing values
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    categorical_cols = df.select_dtypes(include=["object"]).columns

    for col in numeric_cols:
        if df[col].isnull().any():
            df[col] = df[col].fillna(df[col].median())

    for col in categorical_cols:
        if df[col].isnull().any():
            df[col] = df[col].fillna("Unknown")

    logger.info("Filled missing values — numeric: median, categorical: 'Unknown'")
    return df


def encode_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Encode categorical columns as category codes.

    Args:
        df: Input DataFrame

    Returns:
        DataFrame with encoded categoricals
    """
    categorical_cols = df.select_dtypes(include=["object"]).columns.tolist()
    logger.info(f"Encoding {len(categorical_cols)} categorical columns")

    for col in categorical_cols:
        df[col] = df[col].astype("category").cat.codes

    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Main cleaning pipeline. Runs all cleaning steps in order.

    Args:
        df: Raw merged DataFrame from load_data()

    Returns:
        Cleaned DataFrame ready for feature engineering
    """
    logger.info(f"Starting cleaning pipeline — shape: {df.shape}")

    report = get_missing_report(df)
    logger.info(f"Columns with missing values: {len(report)}")

    df = drop_high_missing_columns(df, threshold=0.5)
    logger.info(f"After dropping high-missing columns: {df.shape}")

    df = fill_missing_values(df)
    logger.info(f"Missing values remaining: {df.isnull().sum().sum()}")

    df = encode_categoricals(df)
    logger.info(f"Cleaning complete — final shape: {df.shape}")

    return df


def save_processed(
    df: pd.DataFrame,
    output_path: str = "data/processed/train_clean.parquet"
) -> None:
    """
    Save cleaned DataFrame as parquet.
    Parquet is faster and smaller than CSV for large datasets.

    Args:
        df: Cleaned DataFrame
        output_path: Where to save
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)
    logger.info(f"Saved cleaned data to {output_path}")


if __name__ == "__main__":
    logger.info("=== Starting Data Cleaning Pipeline ===")
    df_raw = load_data()
    df_clean = clean_data(df_raw)
    save_processed(df_clean)
    print(f"\nCleaned dataset shape: {df_clean.shape}")
    print(f"Fraud rate preserved: {df_clean['isFraud'].mean():.2%}")