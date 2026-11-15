"""
CineMatch AI - SQLite Database Manager Module
Manages local persistence for custom ratings, favorite genres, and bookmarks.
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime

from src.utils import get_paths, setup_logger

logger = setup_logger("db")


def get_db_path() -> Path:
    """Returns the path to the SQLite database file."""
    paths = get_paths()
    db_dir = paths["database"]
    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir / "cinematch.db"


def get_connection() -> sqlite3.Connection:
    """Returns an open connection to SQLite with row-factory enabled."""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initializes tables if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # Table: Custom Ratings
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS custom_ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            movie_id INTEGER NOT NULL,
            rating REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, movie_id)
        )
    """)

    # Table: User Preferences
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id TEXT PRIMARY KEY,
            favorite_genres TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Table: Bookmarks
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_bookmarks (
            user_id TEXT NOT NULL,
            movie_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY(user_id, movie_id)
        )
    """)

    conn.commit()
    conn.close()
    logger.info("Database initialized successfully.")


def save_rating(user_id: str, movie_id: int, rating: float) -> None:
    """Inserts or updates a user rating for a movie."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO custom_ratings (user_id, movie_id, rating, created_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(user_id, movie_id) DO UPDATE SET
            rating = excluded.rating,
            created_at = CURRENT_TIMESTAMP
    """, (str(user_id), int(movie_id), float(rating)))
    conn.commit()
    conn.close()
    logger.info(f"Saved rating {rating} for movie {movie_id} by user {user_id}")


def get_user_ratings(user_id: str) -> Dict[int, float]:
    """Retrieves all custom ratings for a user as {movie_id: rating}."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT movie_id, rating FROM custom_ratings WHERE user_id = ?",
        (str(user_id),)
    )
    rows = cursor.fetchall()
    conn.close()
    return {row["movie_id"]: row["rating"] for row in rows}


def save_preferences(user_id: str, favorite_genres: List[str]) -> None:
    """Saves user favorite genres as JSON list."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    genres_json = json.dumps(favorite_genres)
    cursor.execute("""
        INSERT INTO user_preferences (user_id, favorite_genres, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(user_id) DO UPDATE SET
            favorite_genres = excluded.favorite_genres,
            updated_at = CURRENT_TIMESTAMP
    """, (str(user_id), genres_json))
    conn.commit()
    conn.close()


def get_preferences(user_id: str) -> List[str]:
    """Retrieves favorite genres for a user."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT favorite_genres FROM user_preferences WHERE user_id = ?",
        (str(user_id),)
    )
    row = cursor.fetchone()
    conn.close()
    if row and row["favorite_genres"]:
        try:
            return json.loads(row["favorite_genres"])
        except Exception:
            return []
    return []


def reset_user_data(user_id: str) -> None:
    """Clears all ratings, preferences, and bookmarks for a user."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM custom_ratings WHERE user_id = ?", (str(user_id),))
    cursor.execute("DELETE FROM user_preferences WHERE user_id = ?", (str(user_id),))
    cursor.execute("DELETE FROM user_bookmarks WHERE user_id = ?", (str(user_id),))
    conn.commit()
    conn.close()
    logger.info(f"Reset all data for user {user_id}")


def toggle_bookmark(user_id: str, movie_id: int) -> bool:
    """Toggles bookmark status for a movie. Returns True if now bookmarked, False if removed."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM user_bookmarks WHERE user_id = ? AND movie_id = ?",
        (str(user_id), int(movie_id))
    )
    exists = cursor.fetchone()
    if exists:
        cursor.execute(
            "DELETE FROM user_bookmarks WHERE user_id = ? AND movie_id = ?",
            (str(user_id), int(movie_id))
        )
        bookmarked = False
    else:
        cursor.execute(
            "INSERT INTO user_bookmarks (user_id, movie_id) VALUES (?, ?)",
            (str(user_id), int(movie_id))
        )
        bookmarked = True
    conn.commit()
    conn.close()
    return bookmarked


def get_bookmarks(user_id: str) -> List[int]:
    """Retrieves all bookmarked movie IDs for a user."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT movie_id FROM user_bookmarks WHERE user_id = ? ORDER BY created_at DESC",
        (str(user_id),)
    )
    rows = cursor.fetchall()
    conn.close()
    return [row["movie_id"] for row in rows]
