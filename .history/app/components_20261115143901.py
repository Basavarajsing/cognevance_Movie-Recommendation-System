"""
CineMatch AI - Reusable UI Components Module
Contains realistic movie cards, SVG posters, KPI metric cards, and layout elements.
Uses st.html() to guarantee zero Markdown code-block escaping.
"""

import base64
import html
import urllib.parse
from typing import List, Dict, Optional, Any
import pandas as pd
import streamlit as st

try:
    from src.poster_generator import generate_movie_poster as _generate_movie_poster
except ImportError:  # pragma: no cover - fallback when Pillow isn't installed yet
    _generate_movie_poster = None

# Color palettes & aesthetic iconography for genres
GENRE_THEMES = {
    "Action": {
        "grad": ("#B91C1C", "#EA580C"),
        "icon": '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>'
    },
    "Adventure": {
        "grad": ("#0369A1", "#0284C7"),
        "icon": '<circle cx="12" cy="12" r="10"></circle><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"></polygon>'
    },
    "Animation": {
        "grad": ("#D97706", "#EC4899"),
        "icon": '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>'
    },
    "Children's": {
        "grad": ("#059669", "#3B82F6"),
        "icon": '<path d="M12 3v18M3 12h18"></path>'
    },
    "Comedy": {
        "grad": ("#7C3AED", "#DB2777"),
        "icon": '<circle cx="12" cy="12" r="10"></circle><path d="M8 14s1.5 2 4 2 4-2 4-2"></path><line x1="9" y1="9" x2="9.01" y2="9"></line><line x1="15" y1="9" x2="15.01" y2="9"></line>'
    },
    "Crime": {
        "grad": ("#334155", "#0F172A"),
        "icon": '<circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line>'
    },
    "Documentary": {
        "grad": ("#0F766E", "#06B6D4"),
        "icon": '<circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line>'
    },
    "Drama": {
        "grad": ("#4F46E5", "#7C3AED"),
        "icon": '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>'
    },
    "Fantasy": {
        "grad": ("#9333EA", "#4F46E5"),
        "icon": '<polygon points="12 2 15 9 22 9 17 14 19 21 12 17 5 21 7 14 2 9 9 9 12 2"></polygon>'
    },
    "Film-Noir": {
        "grad": ("#18181B", "#3F3F46"),
        "icon": '<circle cx="12" cy="12" r="10"></circle><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"></line>'
    },
    "Horror": {
        "grad": ("#881337", "#1E1B4B"),
        "icon": '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>'
    },
    "Musical": {
        "grad": ("#BE185D", "#E11D48"),
        "icon": '<path d="M9 18V5l12-2v13"></path><circle cx="6" cy="18" r="3"></circle><circle cx="18" cy="16" r="3"></circle>'
    },
    "Mystery": {
        "grad": ("#3730A3", "#1E1B4B"),
        "icon": '<circle cx="12" cy="12" r="10"></circle><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path><line x1="12" y1="17" x2="12.01" y2="17"></line>'
    },
    "Romance": {
        "grad": ("#E11D48", "#F43F5E"),
        "icon": '<path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>'
    },
    "Sci-Fi": {
        "grad": ("#1D4ED8", "#06B6D4"),
        "icon": '<circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="4"></circle><line x1="4.93" y1="4.93" x2="9.17" y2="9.17"></line><line x1="14.83" y1="14.83" x2="19.07" y2="19.07"></line>'
    },
    "Thriller": {
        "grad": ("#7F1D1D", "#451A03"),
        "icon": '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>'
    },
    "War": {
        "grad": ("#44403C", "#1C1917"),
        "icon": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>'
    },
    "Western": {
        "grad": ("#B45309", "#78350F"),
        "icon": '<circle cx="12" cy="12" r="10"></circle><polygon points="12 6 12 18 18 12 12 6"></polygon>'
    },
    "default": {
        "grad": ("#4F46E5", "#7C3AED"),
        "icon": '<rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18"></rect><line x1="7" y1="2" x2="7" y2="22"></line><line x1="17" y1="2" x2="17" y2="22"></line><line x1="2" y1="12" x2="22" y2="12"></line>'
    }
}


def get_genre_theme(genres_str: str) -> dict:
    """Returns aesthetic color gradient and SVG icon based on primary genre."""
    if not genres_str:
        return GENRE_THEMES["default"]
    first_genre = genres_str.split("|")[0].strip()
    return GENRE_THEMES.get(first_genre, GENRE_THEMES["default"])


def generate_realistic_poster(title: str, genres: str, year: int, rating: Optional[float] = None) -> str:
    """
    Generates a realistic, cinematic SVG movie poster.
    Completely self-contained, offline, and styled like an authentic film poster.
    """
    theme = get_genre_theme(genres)
    c1, c2 = theme["grad"]
    icon_svg = theme["icon"]
    clean_title = html.escape(title[:36] + ("..." if len(title) > 36 else ""))
    first_genre = html.escape(genres.split("|")[0] if genres else "Cinema")

    rating_str = f"★ {rating:.1f}" if rating is not None else "★ 4.0"

    svg_content = f"""<div style="width: 100%; height: 210px; border-radius: 14px 14px 0 0; overflow: hidden; position: relative;
background: linear-gradient(155deg, {c1} 0%, {c2} 60%, #0A0E1A 100%);
box-shadow: inset 0 0 35px rgba(0,0,0,0.65); display: flex; flex-direction: column; justify-content: space-between; padding: 14px; box-sizing: border-box;">
<div style="display: flex; justify-content: space-between; align-items: center; z-index: 2;">
<span style="background: rgba(0,0,0,0.55); backdrop-filter: blur(4px); color: #FFF; padding: 3px 9px; border-radius: 6px; font-size: 11px; font-weight: 800; letter-spacing: 0.5px; border: 1px solid rgba(255,255,255,0.15);">{year}</span>
<span style="background: rgba(255,255,255,0.22); backdrop-filter: blur(4px); color: #FFF; padding: 3px 9px; border-radius: 10px; font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.8px; border: 1px solid rgba(255,255,255,0.2);">{first_genre}</span>
</div>
<div style="text-align: center; margin: auto 0; z-index: 2;">
<svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.85)" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" style="filter: drop-shadow(0 4px 12px rgba(0,0,0,0.5)); margin: 0 auto;">
{icon_svg}
</svg>
</div>
<div style="background: rgba(11, 15, 25, 0.88); backdrop-filter: blur(8px); padding: 8px 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.12); z-index: 2; display: flex; justify-content: space-between; align-items: center;">
<div style="color: #FFFFFF; font-weight: 800; font-size: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 70%;" title="{html.escape(title)}">{clean_title}</div>
<div style="background: rgba(245, 158, 11, 0.2); border: 1px solid rgba(245, 158, 11, 0.5); color: #FBBF24; padding: 1px 7px; border-radius: 6px; font-weight: 800; font-size: 11px;">{rating_str}</div>
</div>
</div>"""
    return svg_content


def render_kpi_card(title: str, value: Any, subtitle: str = "", icon: str = "🎬") -> str:
    """Returns HTML string for a glassmorphism KPI stat card."""
    return f"""<div class="cinematch-metric-card">
<div style="font-size: 1.6rem; margin-bottom: 4px;">{icon}</div>
<div class="cinematch-metric-title">{html.escape(title)}</div>
<div class="cinematch-metric-val">{html.escape(str(value))}</div>
<div class="cinematch-metric-sub">{html.escape(subtitle)}</div>
</div>"""


def render_hero_banner(title: str, subtitle: str) -> None:
    """Renders a cinematic gradient hero banner with high-contrast text."""
    banner_html = f"""<div class="hero-banner">
<h1 class="hero-title">{html.escape(title)}</h1>
<p class="hero-subtitle">{html.escape(subtitle)}</p>
</div>"""
    st.html(banner_html)


def render_movie_card(
    movie: pd.Series,
    show_score: bool = True,
    show_explanation: bool = True,
    rank: Optional[int] = None
) -> None:
    """
    Renders an interactive, realistic cinematic movie card.
    Guaranteed clean layout using st.html() to avoid Markdown code-block escaping.
    """
    title = str(movie.get("clean_title", movie.get("title", "Untitled Movie")))
    year = int(movie.get("year", 1995))
    genres = str(movie.get("genres", "Drama"))
    genre_list = [g.strip() for g in genres.split("|") if g.strip()][:3]

    score = movie.get("recommendation_score", movie.get("predicted_rating", movie.get("avg_rating", None)))
    explanation = movie.get("explanation", None)

    poster_html = generate_realistic_poster(title, genres, year, score)
    if _generate_movie_poster is not None:
        try:
            poster_bytes = _generate_movie_poster(title, genres, year, score, width=320, height=460)
            poster_b64 = base64.b64encode(poster_bytes).decode("ascii")
            safe_title = html.escape(title, quote=True)
            poster_html = (
                f'<img src="data:image/png;base64,{poster_b64}" '
                f'alt="{safe_title}" '
                'style="display:block; width:100%; height:210px; object-fit:cover; '
                'border-radius:14px 14px 0 0; border-bottom:1px solid rgba(255,255,255,0.08);" />'
            )
        except Exception:
            poster_html = generate_realistic_poster(title, genres, year, score)

    rank_badge = f'<span style="background: rgba(139, 92, 246, 0.4); border: 1px solid #8B5CF6; color: #FFF; padding: 2px 7px; border-radius: 6px; font-size: 0.75rem; font-weight: 800; margin-right: 6px;">#{rank}</span>' if rank else ""
    score_html = f'<span class="score-badge-pill">★ {score:.1f}</span>' if (show_score and score is not None) else ""

    pills_html = "".join([f'<span class="genre-badge-item">{html.escape(g)}</span>' for g in genre_list])

    exp_html = ""
    if show_explanation and explanation:
        exp_html = f"""<div class="explanation-callout">
<strong style="color: #C4B5FD;">✦ Why you'll love it:</strong><br/>
{html.escape(explanation)}
</div>"""

    # Direct IMDb Search link URL
    encoded_search = urllib.parse.quote_plus(f"{title} {year}")
    imdb_search_url = f"https://www.imdb.com/find?q={encoded_search}"

    card_html = f"""<div class="movie-card-container">
{poster_html}
<div class="movie-card-body">
<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
<div style="flex: 1; min-width: 0; padding-right: 8px;">
<h4 class="movie-title-text" title="{html.escape(title)}">{rank_badge}{html.escape(title)}</h4>
<span class="movie-year-tag">{year}</span>
</div>
<div>{score_html}</div>
</div>
<div class="genre-pills-row">
{pills_html}
</div>
{exp_html}
<div class="card-actions-row">
<a href="{imdb_search_url}" target="_blank" class="card-action-btn">🔗 View IMDb</a>
</div>
</div>
</div>"""

    st.html(card_html)
