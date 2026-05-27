# Modeling

## Problem Definition

- Task: binary fraud classification
- Dataset: IEEE-CIS Fraud Detection
- Target: `isFraud`
- Objective: rank and flag risky transactions for downstream review

## Feature Engineering

Feature generation is handled in `src/features/build_features.py`.

- Detects target column from configured candidates
- Removes leakage and excluded columns before modeling
- Preserves raw feature columns for training-time preprocessing
- Writes `data/processed/features.csv` and feature metadata

## Leakage Prevention

Leakage controls are explicit:

- `TransactionID` is excluded (`features.leakage_columns`)
- Target column is removed from `X`
- Optional configured drop columns are excluded

This keeps training and inference aligned with realistic, pre-outcome information.

## Training Pipeline

`src/models/train.py` builds a reproducible sklearn pipeline:

- Numeric: imputation + optional scaling
- Categorical: imputation + one-hot encoding (`handle_unknown=ignore`)
- Model: logistic regression baseline (configurable)
- Wrapper: `Pipeline` + `ColumnTransformer`

Outputs include model artifact, preprocessor artifact, feature columns, run metadata, and metrics reports.

## Metrics

Primary fraud-facing metrics:

- Precision
- Recall
- F1
- ROC-AUC
- PR-AUC

Accuracy is de-emphasized because fraud detection is class-imbalanced and false negatives are costly.

## Threshold Trade-Offs

`reports/threshold_report.json` summarizes operating points:

- Fixed thresholds (`0.2`, `0.5`, `0.8`, `0.95`)
- Top-k alerting thresholds (capacity-based views)
- Alerts-per-10k volume estimates

This supports business-aligned tuning between recall, precision, and review workload.

## Limitations and Future Improvements

- Current baseline is linear and may miss nonlinear interactions
- Validation is local; no production traffic feedback loop
- Alert rules are deterministic and intentionally simple
- Future improvements could include temporal validation by default, richer feature sets, and calibrated probability workflows
