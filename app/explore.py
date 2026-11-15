"""
CineMatch AI - Explore Movies Page
"""

import streamlit as st
import pandas as pd
from app.components import render_movie_card


def render_explore_page(
    movies_df: pd.DataFrame,
    ratings_df: pd.DataFrame,
    ibcf_model,
    content_model
) -> None:
    st.html("""<div style="margin-bottom: 22px;">
<h2 style="color: #FFFFFF !important; font-size: 2.1rem; font-weight: 800; margin: 0 0 6px 0;">🔍 Explore & Search Movie Catalog</h2>
<p style="color: #94A3B8 !important; font-size: 0.96rem; margin: 0;">Browse 1,682 films, filter by decade & genres, and discover deeply similar movies.</p>
</div>""")

    # Compute movie statistics if not present
    if "vote_count" not in movies_df.columns:
        stats = ratings_df.groupby("movie_id").agg(
            vote_count=("rating", "count"),
            avg_rating=("rating", "mean")
        ).reset_index()
        df = pd.merge(movies_df, stats, on="movie_id", how="left")
        df["vote_count"] = df["vote_count"].fillna(0).astype(int)
        df["avg_rating"] = df["avg_rating"].fillna(0.0).round(2)
    else:
        df = movies_df.copy()

    # Search & Filter Controls
    c_search, c_sort = st.columns([3, 2])
    with c_search:
        search_query = st.text_input("Search by Movie Title:", placeholder="e.g. Star Wars, Toy Story, Pulp Fiction...")
    with c_sort:
        sort_by = st.selectbox(
            "Sort Catalog By:",
            ["Most Rated (Popularity)", "Highest Average Rating", "Newest Release", "Oldest Classic", "Alphabetical (A-Z)"]
        )

    col_g, col_y, col_r = st.columns([2, 2, 2])
    with col_g:
        genre_options = [
            "All", "Action", "Adventure", "Animation", "Children's", "Comedy", "Crime",
            "Documentary", "Drama", "Fantasy", "Film-Noir", "Horror", "Musical",
            "Mystery", "Romance", "Sci-Fi", "Thriller", "War", "Western"
        ]
        selected_genre = st.selectbox("Genre Filter:", genre_options, index=0)
    with col_y:
        min_y, max_y = int(df["year"].min()), int(df["year"].max())
        year_range = st.slider("Release Year Range:", min_y, max_y, (min_y, max_y))
    with col_r:
        min_votes = st.slider("Minimum Rating Count:", 0, 300, 10, step=10)

    # Apply filters
    filtered_df = df.copy()
    if search_query:
        filtered_df = filtered_df[filtered_df["clean_title"].str.contains(search_query, case=False, na=False)]

    if selected_genre != "All":
        if selected_genre in filtered_df.columns:
            filtered_df = filtered_df[filtered_df[selected_genre] == 1]
        else:
            filtered_df = filtered_df[filtered_df["genres"].str.contains(selected_genre, case=False, na=False)]

    filtered_df = filtered_df[
        (filtered_df["year"] >= year_range[0]) &
        (filtered_df["year"] <= year_range[1]) &
        (filtered_df["vote_count"] >= min_votes)
    ]

    # Sort
    if sort_by == "Most Rated (Popularity)":
        filtered_df = filtered_df.sort_values(by="vote_count", ascending=False)
    elif sort_by == "Highest Average Rating":
        filtered_df = filtered_df.sort_values(by="avg_rating", ascending=False)
    elif sort_by == "Newest Release":
        filtered_df = filtered_df.sort_values(by="year", ascending=False)
    elif sort_by == "Oldest Classic":
        filtered_df = filtered_df.sort_values(by="year", ascending=True)
    elif sort_by == "Alphabetical (A-Z)":
        filtered_df = filtered_df.sort_values(by="clean_title", ascending=True)

    st.html(f"<div style='margin: 15px 0 10px 0; color: #E2E8F0; font-weight: 700;'>Showing {len(filtered_df):,} matching movies:</div>")

    # Interactive Movie Inspector & Similar Movies Finder
    if not filtered_df.empty:
        with st.expander("✨ Inspect Movie Details & Find Similar Titles", expanded=True):
            inspect_opts = dict(zip(filtered_df["movie_id"], filtered_df["clean_title"] + f" ({year_range[0]}-{year_range[1]})"))
            selected_inspect_id = st.selectbox(
                "Choose a movie to find similar titles:",
                options=list(inspect_opts.keys())[:100],
                format_func=lambda x: inspect_opts[x]
            )
            target_movie = df[df["movie_id"] == selected_inspect_id].iloc[0]

            col_info, col_sim = st.columns([1, 2])
            with col_info:
                st.html(f"""<div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 16px;">
<h3 style="color: #FFFFFF !important; font-size: 1.3rem; margin: 0 0 8px 0;">{target_movie['clean_title']}</h3>
<p style="color: #94A3B8; margin: 4px 0;"><b>Release Year:</b> <span style="color: #FFFFFF;">{target_movie['year']}</span></p>
<p style="color: #94A3B8; margin: 4px 0;"><b>Genres:</b> <span style="color: #A78BFA;">{target_movie['genres']}</span></p>
<p style="color: #94A3B8; margin: 4px 0;"><b>Community Rating:</b> <span style="color: #FBBF24; font-weight: 800;">★ {target_movie['avg_rating']:.2f} / 5</span> ({int(target_movie['vote_count']):,} votes)</p>
</div>""")
                if pd.notnull(target_movie.get("imdb_url")) and str(target_movie["imdb_url"]).startswith("http"):
                    st.html(f"<div style='margin-top: 8px;'><a href='{target_movie['imdb_url']}' target='_blank' style='color: #38BDF8; font-weight: 700;'>🔗 View on IMDb Database</a></div>")

            with col_sim:
                sim_mode = st.radio("Similarity Method:", ["Item-Based CF (Rating Patterns)", "Content-Based (Genre & Themes)"], horizontal=True)
                if "Item-Based" in sim_mode:
                    similar_movies = ibcf_model.get_similar_items(selected_inspect_id, top_n=3)
                else:
                    similar_movies = content_model.get_similar_movies(selected_inspect_id, top_n=3)

                if similar_movies.empty:
                    st.info("No close similarity matches found for this specific title.")
                else:
                    st.html(f"<div style='margin: 8px 0; color: #FFFFFF; font-weight: 700;'>Top 3 Movies Similar to <em>{target_movie['clean_title']}</em>:</div>")
                    sim_cols = st.columns(3)
                    for idx, (_, sim_row) in enumerate(similar_movies.iterrows()):
                        with sim_cols[idx]:
                            render_movie_card(sim_row, show_score=True, show_explanation=True)

    st.html("<hr style='border-color: rgba(255,255,255,0.08); margin: 25px 0;'>")

    # Paginated Display of Catalog Movies
    display_limit = 12
    display_df = filtered_df.head(display_limit)
    cols = st.columns(3)
    for idx, (_, row) in enumerate(display_df.iterrows()):
        with cols[idx % 3]:
            render_movie_card(row, show_score=True, show_explanation=False)

    if len(filtered_df) > display_limit:
        st.caption(f"Showing top {display_limit} of {len(filtered_df)} titles. Refine search criteria for targeted results.")
