"""
Unit tests for model evaluation metrics and data split integrity.
"""

import pytest
import numpy as np
import pandas as pd

from src.evaluation import compute_rmse, compute_mae, evaluate_top_k
from src.data_loader import load_split


def test_metric_calculations():
    actuals = np.array([4.0, 5.0, 3.0, 2.0])
    predictions = np.array([3.0, 5.0, 4.0, 2.0])

    # Differences: [-1, 0, 1, 0] -> Squared: [1, 0, 1, 0] -> Mean: 0.5 -> RMSE: sqrt(0.5) ~ 0.7071
    rmse = compute_rmse(actuals, predictions)
    assert abs(rmse - np.sqrt(0.5)) < 1e-4

    # Absolute diffs: [1, 0, 1, 0] -> Mean: 0.5 -> MAE: 0.5
    mae = compute_mae(actuals, predictions)
    assert abs(mae - 0.5) < 1e-4


def test_split_leakage_free():
    train_df, test_df = load_split("u1")
    assert len(train_df) == 80000
    assert len(test_df) == 20000

    # Verify disjoint (user_id, movie_id) pairs between train and test
    train_pairs = set(zip(train_df["user_id"], train_df["movie_id"]))
    test_pairs = set(zip(test_df["user_id"], test_df["movie_id"]))

    overlap = train_pairs.intersection(test_pairs)
    assert len(overlap) == 0, f"Data leakage detected! Found {len(overlap)} overlapping user-item interactions."
