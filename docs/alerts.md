# Alerts

## Overview

The alert engine is rule-based and deterministic. It combines risk model output with simple transaction checks to produce analyst-facing alerts.

## Rules

Implemented in `src/alerts/rules.py`:

- Severity buckets from risk score thresholds
- Risk and model-based reason flags
- Transaction-based reason flags (for example large amount, unknown product code)

Default severity thresholds:

- low: `0.2`
- medium: `0.5`
- high: `0.8`
- critical: `0.95`

## Reason Codes

Examples:

- `HIGH_RISK_SCORE`
- `MODEL_FLAGGED_FRAUD`
- `CRITICAL_SEVERITY`
- `LARGE_TRANSACTION_AMOUNT`
- `UNKNOWN_PRODUCT_CODE`
- `MISSING_OPTIONAL_CARD_FIELDS`

## Recommended Actions

Mapped by severity:

- low: monitor
- medium: review
- high: manual review required
- critical: block or escalate immediately

## Storage

Alerts are appended as JSON Lines records in:

- `reports/alerts.jsonl`

This file is generated locally and ignored by git.

## Limitations

- No external notification channels enabled by default
- No deduplication or analyst assignment workflow
- Local file storage is for demo and portfolio usage
