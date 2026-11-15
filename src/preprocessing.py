"""
CineMatch AI - Data Preprocessing Module
Validates, cleans, transforms and saves processed dataset tables.
"""

import re
import json
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import pandas as pd
import numpy as np

from src.utils import get_paths, setup_logger, ensure_directories
from src.data_loader import load_raw_data, GENRE_COLUMNS

logger = setup_logger("preprocessing")


def extract_year_from_title(title: str) -> Tuple[str, Optional[int]]:
    """
    Extracts the release year from title string e.g., 'Toy Story (1995)' -> ('Toy Story', 1995).
    """
    if not isinstance(title, str):
        return "", None
    match = re.search(r"\((\d{4})\)", title)
    if match:
        year = int(match.group(1))
        # Keep clean title without year if desired, or keep original title trimmed
        clean_title = re.sub(r"\s*\(\d{4}\)\s*", "", title).strip()
        return clean_title, year
    return title.strip(), None


def build_genre_string(row: pd.Series) -> str:
    """Concatenates active genres into a pipe-separated string."""
    active_genres = [g for g in GENRE_COLUMNS if g != "unknown" and row.get(g, 0) == 1]
    if not active_genres:
        return "Unknown"
    return "|".join(active_genres)


def run_preprocessing() -> Dict[str, Any]:
    """
    Executes full data validation and cleaning pipeline, saving clean
    dataframes into dataset/processed/.
    """
    paths = get_paths()
    ensure_directories()
    proc_dir = paths["dataset_processed"]

    logger.info("Starting data preprocessing...")
    ratings, movies, users = load_raw_data()

    initial_counts = {
        "raw_ratings": len(ratings),
        "raw_movies": len(movies),
        "raw_users": len(users),
    }

    # 1. Ratings Validation
    ratings_nulls = ratings.isnull().sum().to_dict()
    # Ensure proper data types
    ratings["user_id"] = ratings["user_id"].astype(int)
    ratings["movie_id"] = ratings["movie_id"].astype(int)
    ratings["rating"] = ratings["rating"].astype(float)
    ratings["timestamp"] = ratings["timestamp"].astype(int)

    # Valid rating check (1 to 5)
    valid_mask = (ratings["rating"] >= 1.0) & (ratings["rating"] <= 5.0)
    ratings = ratings[valid_mask]

    # Deduplicate: if duplicate (user_id, movie_id) exists, keep latest timestamp
    duplicate_ratings_count = ratings.duplicated(subset=["user_id", "movie_id"]).sum()
    if duplicate_ratings_count > 0:
        ratings = ratings.sort_values("timestamp").drop_duplicates(
            subset=["user_id", "movie_id"], keep="last"
        )

    # Convert timestamp to human-readable datetime
    ratings["datetime"] = pd.to_datetime(ratings["timestamp"], unit="s")

    # 2. Movies Validation & Feature Engineering
    movies_nulls = movies.isnull().sum().to_dict()
    movies["movie_id"] = movies["movie_id"].astype(int)

    # Extract year from title or release_date
    clean_titles = []
    extracted_years = []
    for _, row in movies.iterrows():
        title = str(row["title"])
        c_title, y = extract_year_from_title(title)
        if y is None and pd.notnull(row["release_date"]):
            try:
                y = pd.to_datetime(row["release_date"]).year
            except Exception:
                y = None
        clean_titles.append(c_title)
        extracted_years.append(y)

    movies["clean_title"] = clean_titles
    movies["year"] = extracted_years
    # If any year is missing, fill with median year
    median_year = int(pd.Series(extracted_years).dropna().median())
    movies["year"] = movies["year"].fillna(median_year).astype(int)

    # Build genre string
    movies["genres"] = movies.apply(build_genre_string, axis=1)

    # Drop video_release_date as it is entirely null in MovieLens 100K
    if "video_release_date" in movies.columns:
        movies = movies.drop(columns=["video_release_date"])

    # 3. Users Validation
    users_nulls = users.isnull().sum().to_dict()
    users["user_id"] = users["user_id"].astype(int)
    users["age"] = users["age"].astype(int)
    users["gender"] = users["gender"].str.upper().str.strip()
    users["occupation"] = users["occupation"].str.strip()
    users["zip_code"] = users["zip_code"].astype(str).str.strip()

    # 4. Save Processed Datasets
    ratings_file = proc_dir / "ratings.csv"
    movies_file = proc_dir / "movies.csv"
    users_file = proc_dir / "users.csv"

    ratings.to_csv(ratings_file, index=False)
    movies.to_csv(movies_file, index=False)
    users.to_csv(users_file, index=False)

    summary = {
        "initial_counts": initial_counts,
        "processed_counts": {
            "ratings": len(ratings),
            "movies": len(movies),
            "users": len(users),
        },
        "rating_range": [float(ratings["rating"].min()), float(ratings["rating"].max())],
        "rating_mean": float(ratings["rating"].mean()),
        "rating_std": float(ratings["rating"].std()),
        "year_range": [int(movies["year"].min()), int(movies["year"].max())],
        "null_counts": {
            "ratings": {k: int(v) for k, v in ratings_nulls.items()},
            "movies": {k: int(v) for k, v in movies_nulls.items()},
            "users": {k: int(v) for k, v in users_nulls.items()},
        },
        "duplicates_removed": int(duplicate_ratings_count),
        "genres_list": [g for g in GENRE_COLUMNS if g != "unknown"],
    }

    summary_file = proc_dir / "preprocessing_summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    logger.info(
        f"Preprocessing complete. Clean files written to {proc_dir}. "
        f"Summary: {summary['processed_counts']}"
    )
    return summary


def load_processed_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Loads the cleaned, processed datasets from dataset/processed/.
    If they do not exist yet, triggers preprocessing.
    """
    paths = get_paths()
    proc_dir = paths["dataset_processed"]
    ratings_file = proc_dir / "ratings.csv"
    movies_file = proc_dir / "movies.csv"
    users_file = proc_dir / "users.csv"

    if not (ratings_file.exists() and movies_file.exists() and users_file.exists()):
        run_preprocessing()

    ratings = pd.read_csv(ratings_file)
    movies = pd.read_csv(movies_file)
    users = pd.read_csv(users_file)
    return ratings, movies, users
