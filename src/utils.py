"""
CineMatch AI - Utility Functions and Path Configuration
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import Dict, Any


def get_project_root() -> Path:
    """Return the absolute path to the project root directory."""
    return Path(__file__).resolve().parent.parent


def get_paths() -> Dict[str, Path]:
    """Return a dictionary of standard directory paths for the project."""
    root = get_project_root()
    paths = {
        "root": root,
        "dataset_raw": root / "dataset" / "raw",
        "dataset_processed": root / "dataset" / "processed",
        "ml_100k": root / "ml-100k",
        "models": root / "models",
        "outputs": root / "outputs",
        "charts": root / "outputs" / "charts",
        "reports": root / "outputs" / "reports",
        "recommendations": root / "outputs" / "recommendations",
        "database": root / "database",
        "tests": root / "tests",
    }
    return paths


def ensure_directories() -> None:
    """Ensure all required directories exist."""
    paths = get_paths()
    for name, path in paths.items():
        if name != "root":
            path.mkdir(parents=True, exist_ok=True)


def setup_logger(name: str = "cinematch", level: int = logging.INFO) -> logging.Logger:
    """Configure and return a standardized logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


class Timer:
    """Context manager to measure execution time."""

    def __init__(self, description: str = "Operation"):
        self.description = description
        self.elapsed = 0.0

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed = time.perf_counter() - self.start
        logging.info(f"{self.description} completed in {self.elapsed:.2f} seconds.")


def format_stars(rating: float, max_stars: int = 5) -> str:
    """Return star representation for a numeric rating (1-5)."""
    full_stars = int(round(rating))
    empty_stars = max_stars - full_stars
    return "★" * full_stars + "☆" * max(0, empty_stars)
