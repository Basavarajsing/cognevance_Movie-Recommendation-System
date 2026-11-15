"""
CineMatch AI - Home Dashboard Page
"""

import streamlit as st
import pandas as pd
from app.components import render_hero_banner, render_kpi_card, render_movie_card


def render_home_page(ratings_df: pd.DataFrame, movies_df: pd.DataFrame, pop_model) -> None:
    """Renders the Home Dashboard page with high-contrast cinematic visuals."""
    render_hero_banner(
        title="CineMatch AI",
        subtitle="Next-Generation Intelligent Movie Recommendation Engine powered by Hybrid Machine Learning, Collaborative Filtering, and Content Affinity Modeling."
    )

    # KPI Statistics Row
    total_ratings = len(ratings_df)
    total_movies = len(movies_df)
    total_users = ratings_df["user_id"].nunique()
    avg_rating = ratings_df["rating"].mean()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.html(render_kpi_card("Catalog Movies", f"{total_movies:,}", "Total Curated Titles", "🎬"))
    with col2:
        st.html(render_kpi_card("Active Users", f"{total_users:,}", "MovieLens Cohort", "👥"))
    with col3:
        st.html(render_kpi_card("Ratings Logged", f"{total_ratings:,}", "Verified Reviews", "⭐"))
    with col4:
        st.html(render_kpi_card("Average Rating", f"{avg_rating:.2f} / 5", "Community Sentiment", "✨"))

    st.html("<div style='height: 24px;'></div>")

    # Section 1: Trending & Most Popular Movies
    st.html("""<div style="margin: 20px 0 6px 0;">
<h3 style="color: #FFFFFF !important; font-size: 1.4rem; font-weight: 800; margin: 0;">🔥 Trending Community Favorites</h3>
<p style="color: #94A3B8 !important; font-size: 0.88rem; margin: 2px 0 12px 0;">Top movies by total rating volume and community engagement across the MovieLens 100K catalog.</p>
</div>""")

    top_popular = pop_model.get_most_rated(top_n=6)
    cols = st.columns(3)
    for idx, (_, row) in enumerate(top_popular.iterrows()):
        with cols[idx % 3]:
            render_movie_card(row, show_score=True, show_explanation=False, rank=idx + 1)

    st.html("<div style='height: 20px;'></div>")

    # Section 2: Highest Acclaimed Masterpieces (Bayesian Weighted)
    st.html("""<div style="margin: 20px 0 6px 0;">
<h3 style="color: #FFFFFF !important; font-size: 1.4rem; font-weight: 800; margin: 0;">🏆 Highest Acclaimed Titles</h3>
<p style="color: #94A3B8 !important; font-size: 0.88rem; margin: 2px 0 12px 0;">Movies ranked by Bayesian weighted rating formula (preventing low-sample bias).</p>
</div>""")

    top_acclaimed = pop_model.get_highest_rated(top_n=6, min_votes=50)
    cols_acc = st.columns(3)
    for idx, (_, row) in enumerate(top_acclaimed.iterrows()):
        with cols_acc[idx % 3]:
            render_movie_card(row, show_score=True, show_explanation=False, rank=idx + 1)

    st.html("<div style='height: 24px;'></div>")

    # Section 3: Architecture & Capabilities Overview
    st.html("""<div style="margin: 20px 0 12px 0;">
<h3 style="color: #FFFFFF !important; font-size: 1.4rem; font-weight: 800; margin: 0;">⚡ AI Recommendation Engines Under the Hood</h3>
</div>""")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.info("**User-Based CF**\n\nFinds peers with similar taste via mean-centered cosine similarity and predicts unseen titles.")
    with c2:
        st.info("**Item-Based CF**\n\nDiscovers deep rating patterns between movies using adjusted cosine similarity.")
    with c3:
        st.info("**Content / Genre**\n\nBuilds a dynamic user profile vector against 19 multi-hot genres and TF-IDF title tokens.")
    with c4:
        st.info("**Adaptive Hybrid**\n\nDynamically blends CF, Content, and Popularity weights with cold-start fallbacks.")
