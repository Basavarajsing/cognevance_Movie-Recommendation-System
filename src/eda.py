"""
CineMatch AI - Exploratory Data Analysis & Visualization Module
Generates 10 publication-quality charts (PNG) and interactive Plotly figures.
"""

from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from src.utils import get_paths, setup_logger, ensure_directories
from src.preprocessing import load_processed_data
from src.data_loader import GENRE_COLUMNS

logger = setup_logger("eda")

# Dark Theme styling constants for publication charts
BG_COLOR = "#0F172A"
PANEL_COLOR = "#1E293B"
TEXT_COLOR = "#F8FAFC"
GRID_COLOR = "#334155"
ACCENT_PURPLE = "#8B5CF6"
ACCENT_BLUE = "#3B82F6"
ACCENT_CYAN = "#06B6D4"
ACCENT_PINK = "#EC4899"
ACCENT_AMBER = "#F59E0B"
PALETTE = ["#8B5CF6", "#3B82F6", "#06B6D4", "#10B981", "#F59E0B", "#EC4899", "#A855F7"]


def apply_dark_theme(ax: plt.Axes, title: str = "", xlabel: str = "", ylabel: str = "") -> None:
    """Applies a sleek modern dark theme to a matplotlib axis."""
    ax.set_facecolor(PANEL_COLOR)
    ax.figure.patch.set_facecolor(BG_COLOR)
    ax.tick_params(colors=TEXT_COLOR, labelsize=10)
    ax.xaxis.label.set_color(TEXT_COLOR)
    ax.yaxis.label.set_color(TEXT_COLOR)
    ax.title.set_color(TEXT_COLOR)
    ax.title.set_fontsize(13)
    ax.title.set_fontweight("bold")
    ax.grid(True, linestyle="--", alpha=0.3, color=GRID_COLOR)
    for spine in ax.spines.values():
        spine.set_color(GRID_COLOR)
        spine.set_linewidth(1.0)
    if title:
        ax.set_title(title, pad=12)
    if xlabel:
        ax.set_xlabel(xlabel, labelpad=8)
    if ylabel:
        ax.set_ylabel(ylabel, labelpad=8)


def generate_all_charts() -> Dict[str, str]:
    """
    Generates all 10 required EDA charts and saves them to outputs/charts/.
    Returns a dict mapping chart keys to file paths.
    """
    paths = get_paths()
    ensure_directories()
    charts_dir = paths["charts"]
    ratings, movies, users = load_processed_data()

    logger.info("Generating 10 comprehensive EDA charts...")
    chart_paths = {}

    # Merge ratings with movie title & genre
    rm_df = pd.merge(ratings, movies[["movie_id", "title", "clean_title", "year", "genres"]], on="movie_id", how="left")

    # 1. Top 10 Most-Rated Movies
    fig, ax = plt.subplots(figsize=(10, 5.5))
    top_most_rated = rm_df.groupby("clean_title")["rating"].count().nlargest(10).sort_values()
    bars = ax.barh(top_most_rated.index, top_most_rated.values, color=ACCENT_PURPLE, edgecolor="#A78BFA", alpha=0.88)
    apply_dark_theme(ax, "Top 10 Most-Rated Movies in MovieLens 100K", "Number of Ratings", "Movie Title")
    for bar in bars:
        w = bar.get_width()
        ax.text(w + 5, bar.get_y() + bar.get_height() / 2, f"{int(w):,}", va="center", color=TEXT_COLOR, fontsize=9)
    plt.tight_layout()
    p1 = charts_dir / "chart_1_top_10_most_rated.png"
    plt.savefig(p1, dpi=300, facecolor=BG_COLOR)
    plt.close()
    chart_paths["top_10_most_rated"] = str(p1)

    # 2. Top 10 Highest-Rated Movies (min 50 votes)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    movie_stats = rm_df.groupby("clean_title")["rating"].agg(["count", "mean"])
    filtered_highest = movie_stats[movie_stats["count"] >= 50]["mean"].nlargest(10).sort_values()
    bars = ax.barh(filtered_highest.index, filtered_highest.values, color=ACCENT_CYAN, edgecolor="#67E8F9", alpha=0.88)
    apply_dark_theme(ax, "Top 10 Highest-Rated Movies (Min 50 Ratings)", "Average Rating (1-5 Scale)", "Movie Title")
    ax.set_xlim(3.5, 5.0)
    for bar in bars:
        w = bar.get_width()
        ax.text(w + 0.02, bar.get_y() + bar.get_height() / 2, f"{w:.2f} ★", va="center", color=TEXT_COLOR, fontsize=9)
    plt.tight_layout()
    p2 = charts_dir / "chart_2_top_10_highest_rated.png"
    plt.savefig(p2, dpi=300, facecolor=BG_COLOR)
    plt.close()
    chart_paths["top_10_highest_rated"] = str(p2)

    # 3. Genre Distribution Across Catalog
    fig, ax = plt.subplots(figsize=(10, 6))
    active_genres = [g for g in GENRE_COLUMNS if g != "unknown"]
    genre_counts = movies[active_genres].sum().sort_values()
    bars = ax.barh(genre_counts.index, genre_counts.values, color=ACCENT_BLUE, edgecolor="#93C5FD", alpha=0.85)
    apply_dark_theme(ax, "Movie Count by Genre in Catalog", "Total Movies", "Genre")
    for bar in bars:
        w = bar.get_width()
        ax.text(w + 5, bar.get_y() + bar.get_height() / 2, f"{int(w)}", va="center", color=TEXT_COLOR, fontsize=9)
    plt.tight_layout()
    p3 = charts_dir / "chart_3_genre_distribution.png"
    plt.savefig(p3, dpi=300, facecolor=BG_COLOR)
    plt.close()
    chart_paths["genre_distribution"] = str(p3)

    # 4. Distribution of Movie Ratings (1 to 5)
    fig, ax = plt.subplots(figsize=(8, 5))
    rating_counts = ratings["rating"].value_counts().sort_index()
    bars = ax.bar(rating_counts.index.astype(str), rating_counts.values, color=PALETTE[:5], edgecolor=TEXT_COLOR, alpha=0.85, width=0.6)
    apply_dark_theme(ax, "Distribution of Movie Ratings (1 to 5 Stars)", "Rating (Stars)", "Frequency Count")
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 800, f"{int(h):,} ({h/len(ratings)*100:.1f}%)", ha="center", color=TEXT_COLOR, fontsize=9)
    plt.tight_layout()
    p4 = charts_dir / "chart_4_rating_distribution.png"
    plt.savefig(p4, dpi=300, facecolor=BG_COLOR)
    plt.close()
    chart_paths["rating_distribution"] = str(p4)

    # 5. Number of Ratings per User
    fig, ax = plt.subplots(figsize=(9, 5))
    user_counts = ratings.groupby("user_id")["rating"].count()
    ax.hist(user_counts.values, bins=40, color=ACCENT_PINK, edgecolor=PANEL_COLOR, alpha=0.85)
    ax.axvline(user_counts.median(), color=ACCENT_CYAN, linestyle="--", linewidth=2, label=f"Median: {user_counts.median():.0f}")
    ax.axvline(user_counts.mean(), color=ACCENT_AMBER, linestyle=":", linewidth=2, label=f"Mean: {user_counts.mean():.1f}")
    apply_dark_theme(ax, "Distribution of Ratings per User", "Number of Ratings Submitted by User", "Count of Users")
    ax.legend(facecolor=PANEL_COLOR, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR)
    plt.tight_layout()
    p5 = charts_dir / "chart_5_ratings_per_user.png"
    plt.savefig(p5, dpi=300, facecolor=BG_COLOR)
    plt.close()
    chart_paths["ratings_per_user"] = str(p5)

    # 6. Number of Ratings per Movie
    fig, ax = plt.subplots(figsize=(9, 5))
    movie_counts = ratings.groupby("movie_id")["rating"].count()
    ax.hist(movie_counts.values, bins=45, color=ACCENT_AMBER, edgecolor=PANEL_COLOR, alpha=0.85)
    ax.axvline(movie_counts.median(), color=ACCENT_CYAN, linestyle="--", linewidth=2, label=f"Median: {movie_counts.median():.0f}")
    ax.axvline(movie_counts.mean(), color=ACCENT_PURPLE, linestyle=":", linewidth=2, label=f"Mean: {movie_counts.mean():.1f}")
    apply_dark_theme(ax, "Distribution of Ratings per Movie (Long-Tail)", "Number of Ratings Received", "Count of Movies")
    ax.legend(facecolor=PANEL_COLOR, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR)
    plt.tight_layout()
    p6 = charts_dir / "chart_6_ratings_per_movie.png"
    plt.savefig(p6, dpi=300, facecolor=BG_COLOR)
    plt.close()
    chart_paths["ratings_per_movie"] = str(p6)

    # 7. Most Popular Genres by Total Ratings and Avg Score
    fig, ax1 = plt.subplots(figsize=(11, 5.5))
    genre_data = []
    for g in active_genres:
        mids = movies[movies[g] == 1]["movie_id"]
        g_ratings = ratings[ratings["movie_id"].isin(mids)]["rating"]
        if not g_ratings.empty:
            genre_data.append({
                "genre": g,
                "ratings_count": len(g_ratings),
                "avg_rating": g_ratings.mean()
            })
    gdf = pd.DataFrame(genre_data).sort_values(by="ratings_count", ascending=False)
    x = np.arange(len(gdf))
    width = 0.45
    bars = ax1.bar(x, gdf["ratings_count"], width, color=ACCENT_BLUE, alpha=0.85, label="Total Ratings")
    ax1.set_ylabel("Total Ratings Volume", color=ACCENT_BLUE)
    ax1.tick_params(axis="y", labelcolor=ACCENT_BLUE)
    ax1.set_xticks(x)
    ax1.set_xticklabels(gdf["genre"], rotation=45, ha="right", color=TEXT_COLOR)

    ax2 = ax1.twinx()
    line = ax2.plot(x, gdf["avg_rating"], color=ACCENT_PINK, marker="o", linewidth=2.2, label="Average Rating")
    ax2.set_ylabel("Average Rating (1-5)", color=ACCENT_PINK)
    ax2.tick_params(axis="y", labelcolor=ACCENT_PINK)
    ax2.set_ylim(2.5, 4.5)
    apply_dark_theme(ax1, "Popular Genres: Total Ratings vs. Average Rating", "Genre", "Total Ratings")
    plt.tight_layout()
    p7 = charts_dir / "chart_7_popular_genres_comparison.png"
    plt.savefig(p7, dpi=300, facecolor=BG_COLOR)
    plt.close()
    chart_paths["popular_genres_comparison"] = str(p7)

    # 8. Movie Release-Year Trends
    fig, ax = plt.subplots(figsize=(10, 5))
    year_counts = movies[movies["year"] >= 1920].groupby("year")["movie_id"].count()
    ax.plot(year_counts.index, year_counts.values, color=ACCENT_CYAN, linewidth=2.5, marker=".", markersize=6)
    ax.fill_between(year_counts.index, year_counts.values, color=ACCENT_CYAN, alpha=0.2)
    apply_dark_theme(ax, "Movie Releases by Year (1920 - 1998)", "Release Year", "Number of Movies Released")
    plt.tight_layout()
    p8 = charts_dir / "chart_8_release_year_trends.png"
    plt.savefig(p8, dpi=300, facecolor=BG_COLOR)
    plt.close()
    chart_paths["release_year_trends"] = str(p8)

    # 9. User Demographic Activity (Age, Gender, Occupations)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    # Gender pie
    gender_counts = users["gender"].value_counts()
    axes[0].pie(
        gender_counts.values,
        labels=[f"{'Male' if k=='M' else 'Female'} ({v})" for k, v in gender_counts.items()],
        colors=[ACCENT_BLUE, ACCENT_PINK],
        autopct="%1.1f%%",
        textprops={"color": TEXT_COLOR, "fontsize": 11},
        wedgeprops={"edgecolor": PANEL_COLOR, "linewidth": 2}
    )
    axes[0].set_title("User Gender Ratio", color=TEXT_COLOR, fontweight="bold", pad=10)
    axes[0].set_facecolor(PANEL_COLOR)

    # Age distribution
    axes[1].hist(users["age"], bins=20, color=ACCENT_PURPLE, edgecolor=PANEL_COLOR, alpha=0.85)
    apply_dark_theme(axes[1], "User Age Distribution", "Age", "User Count")
    fig.patch.set_facecolor(BG_COLOR)
    plt.tight_layout()
    p9 = charts_dir / "chart_9_user_demographics.png"
    plt.savefig(p9, dpi=300, facecolor=BG_COLOR)
    plt.close()
    chart_paths["user_demographics"] = str(p9)

    # 10. Movie Rating Trends Over Time
    fig, ax = plt.subplots(figsize=(10, 5))
    ratings["date_month"] = pd.to_datetime(ratings["timestamp"], unit="s").dt.to_period("M").dt.to_timestamp()
    monthly_stats = ratings.groupby("date_month").agg(
        rating_count=("rating", "count"),
        avg_rating=("rating", "mean")
    )
    ax.plot(monthly_stats.index, monthly_stats["rating_count"], color=ACCENT_PURPLE, linewidth=2.5, marker="s", markersize=6)
    apply_dark_theme(ax, "Monthly Rating Activity Trend (MovieLens 1997-1998)", "Month", "Ratings Submitted")
    plt.tight_layout()
    p10 = charts_dir / "chart_10_rating_trends_over_time.png"
    plt.savefig(p10, dpi=300, facecolor=BG_COLOR)
    plt.close()
    chart_paths["rating_trends_over_time"] = str(p10)

    logger.info(f"Successfully generated all {len(chart_paths)} charts in {charts_dir}")
    return chart_paths
