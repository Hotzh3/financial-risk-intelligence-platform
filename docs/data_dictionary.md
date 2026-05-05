# Data Dictionary - Financial Risk Intelligence Platform

This document describes the core fields expected during Phase 1 (`Data + EDA`).
The project currently supports common fraud datasets such as:

- Credit Card Fraud Detection (`creditcard.csv`)
- IEEE-CIS Fraud Detection (`train_transaction.csv`)

## Main Columns (Common Across Fraud Datasets)

- `target` / `isFraud` / `Class`: binary label (1 = fraud, 0 = non-fraud).
- `Amount` or `TransactionAmt`: transaction amount.
- `Time` or `TransactionDT`: transaction time reference (often seconds from a start point).

## Typical Dataset-Specific Columns

### Credit Card Fraud Detection

- `V1 ... V28`: PCA-transformed anonymized features.
- `Amount`: raw transaction amount.
- `Time`: seconds elapsed between this transaction and the first transaction.
- `Class`: target column (`1` fraud, `0` non-fraud).

### IEEE-CIS Fraud Detection

- `TransactionID`: unique transaction id.
- `TransactionDT`: relative transaction timestamp.
- `TransactionAmt`: transaction amount.
- `ProductCD`: product category.
- `card1 ... card6`: card-related attributes.
- `addr1`, `addr2`: anonymized address indicators.
- `dist1`, `dist2`: distance-related engineered variables.
- `P_emaildomain`, `R_emaildomain`: purchaser and recipient email domains.
- `C1 ... C14`, `D1 ... D15`, `M1 ... M9`, `V1 ... V339`: anonymized engineered features.
- `isFraud`: target column (`1` fraud, `0` non-fraud).

## Target Definition

Fraud detection is modeled as a binary classification task:

- `1`: fraudulent transaction
- `0`: legitimate transaction

Important: fraud datasets are usually highly imbalanced, so metrics like precision,
recall, PR-AUC, and ROC-AUC are more informative than accuracy alone.

## Dataset Limitations

- Heavy class imbalance (very few fraud cases).
- Many anonymized features limit direct business interpretation.
- Some datasets use relative time instead of real calendar timestamps.
- Potential drift: fraud patterns change over time.
- Public datasets may not reflect current production fraud behavior in all regions.

## Candidate Features for Phase 2 (Not Implemented Yet)

- Log transform of amount (for skewed distributions).
- Time-based features:
  - hour bucket
  - day-part (morning, afternoon, night)
  - transaction velocity per entity
- Aggregations by card/user/device:
  - count in rolling windows
  - mean/std/max transaction amount
- Risk flags:
  - unusually high amount vs historical profile
  - abnormal transaction timing
