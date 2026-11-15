"""
Unit tests for data loader and preprocessing modules.
"""

import pytest
import pandas as pd
from pathlib import Path

from src.data_loader import load_raw_data, GENRE_COLUMNS, sync_raw_dataset
from src.preprocessing import extract_year_from_title, build_genre_string, run_preprocessing, load_processed_data
from src.utils import get_paths


def test_sync_and_load_raw_data():
    raw_dir = sync_raw_dataset()
    assert (raw_dir / "u.data").exists()
    assert (raw_dir / "u.item").exists()
    assert (raw_dir / "u.user").exists()

    ratings, movies, users = load_raw_data()
    assert len(ratings) == 100000
    assert len(movies) == 1682
    assert len(users) == 943
    assert set(["user_id", "movie_id", "rating", "timestamp"]).issubset(ratings.columns)


def test_extract_year_from_title():
    clean_title, year = extract_year_from_title("Toy Story (1995)")
    assert clean_title == "Toy Story"
    assert year == 1995

    clean_title2, year2 = extract_year_from_title("Seven (Se7en) (1995)")
    assert "Seven" in clean_title2
    assert year2 == 1995

    clean_title3, year3 = extract_year_from_title("Movie Without Year")
    assert clean_title3 == "Movie Without Year"
    assert year3 is None


def test_build_genre_string():
    row = pd.Series({"Action": 1, "Adventure": 1, "Comedy": 0, "unknown": 0})
    genre_str = build_genre_string(row)
    assert "Action" in genre_str
    assert "Adventure" in genre_str
    assert "Comedy" not in genre_str


def test_run_preprocessing_and_schema():
    summary = run_preprocessing()
    assert summary["processed_counts"]["ratings"] > 90000
    assert summary["processed_counts"]["movies"] == 1682
    assert summary["processed_counts"]["users"] == 943

    ratings, movies, users = load_processed_data()
    assert (ratings["rating"] >= 1.0).all() and (ratings["rating"] <= 5.0).all()
    assert (movies["year"] >= 1900).all()
    assert "genres" in movies.columns
    assert "clean_title" in movies.columns
