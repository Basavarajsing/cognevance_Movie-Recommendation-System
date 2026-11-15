"""
CineMatch AI - Data Loader Module
Handles loading of raw MovieLens files with appropriate encodings and separators.
"""

import shutil
from pathlib import Path
from typing import Dict, Tuple, Optional
import pandas as pd

from src.utils import get_paths, setup_logger, ensure_directories

logger = setup_logger("data_loader")

GENRE_COLUMNS = [
    "unknown", "Action", "Adventure", "Animation", "Children's",
    "Comedy", "Crime", "Documentary", "Drama", "Fantasy",
    "Film-Noir", "Horror", "Musical", "Mystery", "Romance",
    "Sci-Fi", "Thriller", "War", "Western"
]

ITEM_COLUMNS = [
    "movie_id", "title", "release_date", "video_release_date", "imdb_url"
] + GENRE_COLUMNS

RATING_COLUMNS = ["user_id", "movie_id", "rating", "timestamp"]
USER_COLUMNS = ["user_id", "age", "gender", "occupation", "zip_code"]


def sync_raw_dataset() -> Path:
    """
    Ensure the raw dataset is organized into dataset/raw/ without touching
    or modifying the original ml-100k directory.
    """
    paths = get_paths()
    ensure_directories()
    raw_dir = paths["dataset_raw"]
    source_dir = paths["ml_100k"]

    if not source_dir.exists():
        if (raw_dir / "u.data").exists():
            logger.info("Raw dataset already located in dataset/raw/")
            return raw_dir
        raise FileNotFoundError(
            f"MovieLens source directory '{source_dir}' not found."
        )

    # Copy files from ml-100k to dataset/raw/ if not already present
    files_to_sync = [
        "u.data", "u.item", "u.user", "u.genre", "u.occupation", "README",
        "u1.base", "u1.test", "u2.base", "u2.test", "u3.base", "u3.test",
        "u4.base", "u4.test", "u5.base", "u5.test", "ua.base", "ua.test",
        "ub.base", "ub.test"
    ]

    for fname in files_to_sync:
        src_file = source_dir / fname
        dest_file = raw_dir / fname
        if src_file.exists() and not dest_file.exists():
            shutil.copy2(src_file, dest_file)

    logger.info("Synced raw MovieLens dataset into dataset/raw/")
    return raw_dir


def load_raw_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Loads ratings, movies (items), and user demographics from raw files.
    Returns:
        (ratings_df, movies_df, users_df)
    """
    raw_dir = sync_raw_dataset()

    ratings_path = raw_dir / "u.data"
    items_path = raw_dir / "u.item"
    users_path = raw_dir / "u.user"

    # Ratings: tab-separated
    ratings = pd.read_csv(
        ratings_path,
        sep="\t",
        names=RATING_COLUMNS,
        encoding="latin-1",
        engine="python"
    )

    # Movies: pipe-separated, latin-1 encoding
    movies = pd.read_csv(
        items_path,
        sep="|",
        names=ITEM_COLUMNS,
        encoding="latin-1",
        engine="python"
    )

    # Users: pipe-separated
    users = pd.read_csv(
        users_path,
        sep="|",
        names=USER_COLUMNS,
        encoding="latin-1",
        engine="python"
    )

    logger.info(
        f"Loaded raw dataset: {len(ratings):,} ratings, "
        f"{len(movies):,} movies, {len(users):,} users."
    )
    return ratings, movies, users


def load_split(split_name: str = "u1") -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Loads standard train/test split from raw files (e.g., u1.base, u1.test).
    Returns:
        (train_df, test_df)
    """
    raw_dir = sync_raw_dataset()
    train_path = raw_dir / f"{split_name}.base"
    test_path = raw_dir / f"{split_name}.test"

    if not train_path.exists() or not test_path.exists():
        raise FileNotFoundError(f"Split {split_name} not found in {raw_dir}")

    train_df = pd.read_csv(
        train_path,
        sep="\t",
        names=RATING_COLUMNS,
        encoding="latin-1",
        engine="python"
    )
    test_df = pd.read_csv(
        test_path,
        sep="\t",
        names=RATING_COLUMNS,
        encoding="latin-1",
        engine="python"
    )

    logger.info(
        f"Loaded split {split_name}: {len(train_df):,} train ratings, "
        f"{len(test_df):,} test ratings."
    )
    return train_df, test_df
