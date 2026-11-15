"""
CineMatch AI - Genre Explorer Page
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from app.components import render_movie_card
from src.data_loader import GENRE_COLUMNS


def render_genre_explorer_page(
    movies_df: pd.DataFrame,
    ratings_df: pd.DataFrame,
    pop_model
) -> None:
    st.html("""<div style="margin-bottom: 22px;">
<h2 style="color: #FFFFFF !important; font-size: 2.1rem; font-weight: 800; margin: 0 0 6px 0;">🎭 Genre Explorer</h2>
<p style="color: #94A3B8 !important; font-size: 0.96rem; margin: 0;">Deep dive into specialized genres, uncover hidden gems, and explore genre dynamics.</p>
</div>""")

    active_genres = [g for g in GENRE_COLUMNS if g != "unknown"]
    selected_genre = st.selectbox("Select a Genre to Explore:", active_genres, index=active_genres.index("Sci-Fi") if "Sci-Fi" in active_genres else 0)

    # Compute stats for selected genre
    genre_movies = movies_df[movies_df[selected_genre] == 1].copy()
    genre_stats = ratings_df[ratings_df["movie_id"].isin(genre_movies["movie_id"])].groupby("movie_id").agg(
        vote_count=("rating", "count"),
        avg_rating=("rating", "mean")
    ).reset_index()

    merged = pd.merge(genre_movies, genre_stats, on="movie_id", how="left")
    merged["vote_count"] = merged["vote_count"].fillna(0).astype(int)
    merged["avg_rating"] = merged["avg_rating"].fillna(0.0).round(2)

    total_titles = len(merged)
    total_reviews = merged["vote_count"].sum()
    genre_avg = merged["avg_rating"].mean()

    # Genre KPI Row
    k1, k2, k3 = st.columns(3)
    with k1:
        st.metric(f"Total {selected_genre} Titles", f"{total_titles:,}")
    with k2:
        st.metric(f"Total {selected_genre} Ratings", f"{total_reviews:,}")
    with k3:
        st.metric(f"{selected_genre} Average Rating", f"{genre_avg:.2f} ★")

    st.html("<div style='height: 20px;'></div>")

    # Curation Tiers (Tabs)
    tab1, tab2, tab3 = st.tabs(["⭐ Highest Acclaimed", "🔥 Most Popular", "💎 Hidden Gems"])

    with tab1:
        st.html(f"<div style='margin: 10px 0 14px 0; color: #FFFFFF; font-weight: 700; font-size: 1.1rem;'>Top Acclaimed {selected_genre} Films (Min 30 Ratings)</div>")
        acclaimed = merged[merged["vote_count"] >= 30].sort_values(by="avg_rating", ascending=False).head(6)
        if acclaimed.empty:
            acclaimed = merged.sort_values(by="avg_rating", ascending=False).head(6)
        cols = st.columns(3)
        for idx, (_, row) in enumerate(acclaimed.iterrows()):
            with cols[idx % 3]:
                render_movie_card(row, show_score=True, show_explanation=False, rank=idx + 1)

    with tab2:
        st.html(f"<div style='margin: 10px 0 14px 0; color: #FFFFFF; font-weight: 700; font-size: 1.1rem;'>Most Watched & Reviewed {selected_genre} Films</div>")
        popular = merged.sort_values(by="vote_count", ascending=False).head(6)
        cols = st.columns(3)
        for idx, (_, row) in enumerate(popular.iterrows()):
            with cols[idx % 3]:
                render_movie_card(row, show_score=True, show_explanation=False, rank=idx + 1)

    with tab3:
        st.html(f"<div style='margin: 10px 0 14px 0; color: #FFFFFF; font-weight: 700; font-size: 1.1rem;'>Hidden Gems: Acclaimed {selected_genre} Titles with Fewer Total Reviews (15 - 60 ratings)</div>")
        hidden = merged[(merged["vote_count"] >= 15) & (merged["vote_count"] <= 60) & (merged["avg_rating"] >= 3.8)]
        hidden = hidden.sort_values(by="avg_rating", ascending=False).head(6)
        if hidden.empty:
            st.info(f"No specific hidden gems found under strict criteria for {selected_genre}.")
        else:
            cols = st.columns(3)
            for idx, (_, row) in enumerate(hidden.iterrows()):
                with cols[idx % 3]:
                    render_movie_card(row, show_score=True, show_explanation=False, rank=idx + 1)

    # Interactive Rating Distribution Chart
    st.html(f"""<hr style='border-color: rgba(255,255,255,0.08); margin: 30px 0 20px 0;'>
<h3 style='color: #FFFFFF !important; font-size: 1.35rem; font-weight: 800; margin: 0 0 12px 0;'>📊 Rating Distribution for {selected_genre}</h3>""")

    sample_ratings = ratings_df[ratings_df["movie_id"].isin(genre_movies["movie_id"])]["rating"]
    if not sample_ratings.empty:
        r_dist = sample_ratings.value_counts().sort_index().reset_index()
        r_dist.columns = ["Rating", "Count"]
        fig = px.bar(
            r_dist,
            x="Rating",
            y="Count",
            text="Count",
            color="Rating",
            color_continuous_scale="Purples",
            title=f"Distribution of Star Ratings in {selected_genre}",
            template="plotly_dark"
        )
        fig.update_layout(
            paper_bgcolor="#0F172A",
            plot_bgcolor="#1E293B",
            font_color="#F8FAFC"
        )
        st.plotly_chart(fig, use_container_width=True)
