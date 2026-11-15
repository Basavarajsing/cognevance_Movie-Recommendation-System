"""Regression tests for the free poster generator feature."""

import io
from pathlib import Path

from PIL import Image

from src.poster_generator import generate_movie_poster


def test_pillow_is_declared_in_requirements():
    req_text = Path("requirements.txt").read_text(encoding="utf-8")
    assert "pillow" in req_text.lower()


def test_generate_movie_poster_returns_valid_png_bytes():
    poster_bytes = generate_movie_poster("Toy Story", "Animation|Comedy", 1995, 4.8)

    assert isinstance(poster_bytes, (bytes, bytearray))
    assert len(poster_bytes) > 1000

    with Image.open(io.BytesIO(poster_bytes)) as img:
        assert img.format == "PNG"
        assert img.size == (320, 460)
