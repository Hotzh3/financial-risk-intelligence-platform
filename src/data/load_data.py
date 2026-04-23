"""
Data loader for the Financial Risk Intelligence Platform.
Handles ingestion and merging of IEEE-CIS Fraud Detection dataset.
"""

import pandas as pd
import yaml
from pathlib import Path
from src.utils.logger import get_logger

logger = get_logger(__name__)


def load_config(config_path: str = "config/config.yaml") -> dict:
    """
    Load project configuration from YAML file.

    Args:
        config_path: Path to config file

    Returns:
        Configuration dictionary
    """
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    logger.info(f"Config loaded from {config_path}")
    return config


def load_transactions(file_path: str) -> pd.DataFrame:
    """
    Load transaction data from CSV.

    Args:
        file_path: Path to train_transaction.csv

    Returns:
        DataFrame with transaction data
    """
    logger.info(f"Loading transactions from {file_path}...")
    df = pd.read_csv(file_path)
    logger.info(f"Transactions loaded: {df.shape[0]:,} rows x {df.shape[1]} columns")
    return df


def load_identity(file_path: str) -> pd.DataFrame:
    """
    Load identity data from CSV.

    Args:
        file_path: Path to train_identity.csv

    Returns:
        DataFrame with identity data
    """
    logger.info(f"Loading identity data from {file_path}...")
    df = pd.read_csv(file_path)
    logger.info(f"Identity loaded: {df.shape[0]:,} rows x {df.shape[1]} columns")
    return df


def merge_datasets(
    transactions: pd.DataFrame,
    identity: pd.DataFrame,
) -> pd.DataFrame:
    """
    Merge transaction and identity datasets on TransactionID.
    Uses left join to keep all transactions (not all have identity data).

    Args:
        transactions: Transaction DataFrame
        identity: Identity DataFrame

    Returns:
        Merged DataFrame
    """
    logger.info("Merging transactions with identity data...")
    df = transactions.merge(identity, on="TransactionID", how="left")
    logger.info(f"Merged dataset: {df.shape[0]:,} rows x {df.shape[1]} columns")
    match_rate = (df["id_01"].notna().sum() / len(df)) * 100
    logger.info(f"Identity match rate: {match_rate:.1f}%")
    return df


def load_data(config_path: str = "config/config.yaml") -> pd.DataFrame:
    """
    Main function to load and merge all data.

    Args:
        config_path: Path to config file

    Returns:
        Complete merged DataFrame ready for processing
    """
    config = load_config(config_path)

    transactions = load_transactions(config["data"]["train_transaction"])
    identity = load_identity(config["data"]["train_identity"])
    df = merge_datasets(transactions, identity)

    return df


if __name__ == "__main__":
    df = load_data()
    print(f"\nFinal dataset shape: {df.shape}")
    print(f"Fraud rate: {df['isFraud'].mean():.2%}")
    print(f"\nFirst 5 rows:\n{df.head()}")