"""
Feature Engineering for the Financial Risk Intelligence Platform.
Creates domain-specific features for fraud detection.
"""

import pandas as pd
import numpy as np
from src.utils.logger import get_logger

logger = get_logger(__name__)


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extract time-based features from TransactionDT."""
    df['hour'] = (df['TransactionDT'] // 3600) % 24
    df['day_of_week'] = (df['TransactionDT'] // (3600 * 24)) % 7
    df['is_night'] = ((df['hour'] >= 0) & (df['hour'] <= 6)).astype(int)
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    logger.info("Time features added: hour, day_of_week, is_night, is_weekend")
    return df


def add_amount_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create amount-based features."""
    df['log_amount'] = np.log1p(df['TransactionAmt'])
    df['amount_cents'] = (df['TransactionAmt'] % 1).round(2)
    df['is_round_amount'] = (df['amount_cents'] == 0).astype(int)
    logger.info("Amount features added: log_amount, amount_cents, is_round_amount")
    return df


def add_card_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create card-based aggregated features."""
    # Mean amount per card
    card_mean = df.groupby('card1')['TransactionAmt'].transform('mean')
    card_std = df.groupby('card1')['TransactionAmt'].transform('std').fillna(0)
    card_count = df.groupby('card1')['TransactionAmt'].transform('count')

    df['card1_amt_mean'] = card_mean
    df['card1_amt_std'] = card_std
    df['card1_tx_count'] = card_count
    df['amt_deviation'] = (df['TransactionAmt'] - card_mean) / (card_std + 1)

    logger.info("Card features added: card1_amt_mean, card1_amt_std, card1_tx_count, amt_deviation")
    return df


def select_features(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """
    Select final feature set for modeling.
    Based on EDA correlation analysis.

    Returns:
        X: Feature matrix
        y: Target vector
    """
    # Top V-features from EDA
    v_features = ['V45', 'V86', 'V87', 'V44', 'V52',
                  'V51', 'V40', 'V79', 'V39', 'V38']

    # Engineered features
    engineered = [
        'log_amount', 'amount_cents', 'is_round_amount',
        'hour', 'day_of_week', 'is_night', 'is_weekend',
        'card1_amt_mean', 'card1_amt_std', 'card1_tx_count', 'amt_deviation'
    ]

    # Base features
    base = ['TransactionAmt', 'card1', 'card2', 'card3',
            'card5', 'card4', 'card6', 'ProductCD']

    all_features = v_features + engineered + base
    available = [f for f in all_features if f in df.columns]

    logger.info(f"Selected {len(available)} features for modeling")
    X = df[available]
    y = df['isFraud']
    return X, y


def run_feature_engineering(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Main pipeline — runs all feature engineering steps."""
    logger.info(f"Starting feature engineering — shape: {df.shape}")
    df = add_time_features(df)
    df = add_amount_features(df)
    df = add_card_features(df)
    X, y = select_features(df)
    logger.info(f"Feature engineering complete — X: {X.shape}, y: {y.shape}")
    return X, y


if __name__ == "__main__":
    import pandas as pd
    df = pd.read_parquet("data/processed/train_clean.parquet")
    X, y = run_feature_engineering(df)
    print(f"\nFeature matrix: {X.shape}")
    print(f"Target: {y.shape}")
    print(f"\nFeatures:\n{list(X.columns)}")