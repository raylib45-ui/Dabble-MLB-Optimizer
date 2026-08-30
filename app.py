

rick_sanchez_mlb_k_hammer.py

#!/usr/bin/env python3

"""
rick sanchez mlb k hammer

selective MORE / LESS MLB pitcher strikeout model.

result:
  1 = prop won
  0 = prop lost
  blank = future or unsettled

the model does not guarantee wins or place bets.
"""

import argparse
import csv
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass
class Config:
    train_fraction: float = 0.70
    minimum_train: int = 75
    minimum_test: int = 25

    hammer_probability: float = 0.62
    hammer_edge: float = 0.055

    a_plus_probability: float = 0.68
    a_plus_edge: float = 0.08

    max_data_age_minutes: float = 45
    max_lineup_age_minutes: float = 75
    strikeout_rate_prior_sample: float = 80
    batter_faced_prior_sample: float = 12


@dataclass
class PitcherRow:
    raw: dict
    decision_time: datetime
    line: float
    result: Optional[int]

    probability: float = 0.50
    fair_odds: Optional[int] = None
    ev_percent: Optional[float] = None
    tag: str = "PASS"
    reason: str = ""


def parse_time(value: str) -> datetime:
    value = value.strip().replace("Z", "+00:00")
    parsed = datetime.fromisoformat(value)

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return parsed


def number(row: dict, key: str, default: float = 0.0) -> float:
    try:
        value = row.get(key, "")

        if value in ("", None):
            return default

        return float(value)

    except (ValueError, TypeError):
        return default


def parse_result(value: str) -> Optional[int]:
    if value in ("", None):
        return None

    try:
        value = int(float(value))
    except ValueError:
        return None

    if value not in (0, 1):
        return None

    return value


def load_csv(path: str) -> list[PitcherRow]:
    required_columns = {
        "decision_time",
        "event_id",
        "pitcher",
        "team",
        "opponent",
        "line",
        "price_american",
        "season_k9",
        "recent_k9",
        "opponent_k_rate",
        "opponent_bb_rate",
        "expected_bf",
        "recent_bf_per_start",
        "result",
    }

    with open(path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        missing = required_columns - set(reader.fieldnames or [])

        if missing:
            raise ValueError(
                "missing columns: " + ", ".join(sorted(missing))
            )

        rows = []

        for raw in reader:
            rows.append(
                PitcherRow(
                    raw=raw,
                    decision_time=parse_time(raw["decision_time"]),
                    line=number(raw, "line"),
                    result=parse_result(raw.get("result", "")),
                )
            )

    return sorted(rows, key=lambda row: row.decision_time)


def american_to_implied(odds: float) -> float:
    if odds < 0:
        return -odds / (-odds + 100)

    return 100 / (odds + 100)


def probability_to_american(probability: float) -> int:
    probability = max(0.0001, min(0.9999, probability))

    if probability >= 0.50:
        return round(-100 * probability / (1 - probability))

    return round(100 * (1 - probability) / probability)


def devig_probability(side_odds: float, opposite_odds: float) -> float:
    side_probability = american_to_implied(side_odds)
    opposite_probability = american_to_implied(opposite_odds)

    total = side_probability + opposite_probability

    return side_probability / total


def calculate_ev(probability: float, odds: float) -> float:
    if odds > 0:
        decimal_odds = 1 + odds / 100
    else:
        decimal_odds = 1 + 100 / abs(odds)

    return (probability * decimal_odds - 1) * 100


def shrink_rate(
    observed_rate: float,
    sample_size: float,
    prior_rate: float,
    prior_sample: float,
) -> float:
    if sample_size <= 0:
        return prior_rate