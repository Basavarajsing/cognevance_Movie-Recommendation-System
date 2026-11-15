"""
CineMatch AI - Personalized Recommendations Page
"""

import streamlit as st
import pandas as pd
from app.components import render_movie_card
from src.db import save_rating, get_user_ratings, reset_user_data, save_preferences, get_preferences


def render_recommendations_page(
    ratings_df: pd.DataFrame,
    movies_df: pd.DataFrame,
    hybrid_model,
    pop_model,
    ubcf_model,
    ibcf_model,
    content_model
) -> None:
    st.html("""<div style="margin-bottom: 22px;">
<h2 style="color: #FFFFFF !important; font-size: 2.1rem; font-weight: 800; margin: 0 0 6px 0;">🎯 Personalized Movie Recommendations</h2>
<p style="color: #94A3B8 !important; font-size: 0.96rem; margin: 0;">Generate tailored recommendations using multi-algorithmic models with transparent explanations.</p>
</div>""")

    # Top Control Bar: User Selector & Profile Type
    col_user, col_type = st.columns([2, 1])
    with col_user:
        user_mode = st.radio(
            "Select Profile Cohort:",
            ["Existing MovieLens User (ID 1-943)", "Guest / Custom Interactive Profile"],
            horizontal=True
        )

    if user_mode.startswith("Existing"):
        all_user_ids = sorted(ratings_df["user_id"].unique())
        selected_user_id = st.selectbox(
            "Select User ID:",
            all_user_ids,
            index=0,
            help="Select any of the 943 MovieLens users to inspect their history and generate tailored recommendations."
        )
        user_key = str(selected_user_id)
    else:
        selected_user_id = 99999
        user_key = "custom_guest_user"
        st.info("💡 **Custom Profile Active**: Rate movies or pick favorite genres below to test cold-start and real-time adaptation!")

    # Interactive Preference & Quick Rating Drawer
    with st.expander("⭐ Interactive Rating & Preference Studio (Live SQLite Persistence)", expanded=(user_mode.startswith("Guest"))):
        t1, t2 = st.tabs(["Rate a Movie", "Favorite Genres & Reset"])
        with t1:
            movie_options = dict(zip(movies_df["movie_id"], movies_df["clean_title"] + " (" + movies_df["year"].astype(str) + ")"))
            sel_mid = st.selectbox("Choose a Movie to Rate:", options=list(movie_options.keys()), format_func=lambda x: movie_options[x])
            col_r, col_btn = st.columns([3, 1])
            with col_r:
                user_rating = st.slider("Your Rating (Stars):", min_value=1.0, max_value=5.0, value=4.5, step=0.5)
            with col_btn:
                st.html("<div style='height: 28px;'></div>")
                if st.button("Save Rating", key="btn_save_rating"):
                    save_rating(user_key, sel_mid, user_rating)
                    st.success(f"Saved {user_rating}★ for '{movie_options[sel_mid]}'")
                    st.rerun()

            custom_ratings = get_user_ratings(user_key)
            if custom_ratings:
                st.html(f"<div style='margin-top: 10px; color: #E2E8F0; font-weight: 700;'>Your Custom Rated Movies ({len(custom_ratings)}):</div>")
                rated_list = []
                for mid, r in custom_ratings.items():
                    title = movie_options.get(mid, f"Movie {mid}")
                    rated_list.append(f"• <span style='color: #F8FAFC;'><b>{title}</b>: <span style='color:#FBBF24;'>{r:.1f}★</span></span>")
                st.html("<div style='font-size: 0.9rem; margin-top: 4px;'>" + "<br/>".join(rated_list) + "</div>")

        with t2:
            all_genres = [
                "Action", "Adventure", "Animation", "Children's", "Comedy", "Crime",
                "Documentary", "Drama", "Fantasy", "Film-Noir", "Horror", "Musical",
                "Mystery", "Romance", "Sci-Fi", "Thriller", "War", "Western"
            ]
            saved_genres = get_preferences(user_key)
            selected_favs = st.multiselect("Your Favorite Genres:", all_genres, default=saved_genres)
            col_save_g, col_reset = st.columns([1, 1])
            with col_save_g:
                if st.button("Save Genre Preferences"):
                    save_preferences(user_key, selected_favs)
                    st.success("Preferences updated!")
            with col_reset:
                if st.button("Clear / Reset All Custom Data", type="secondary"):
                    reset_user_data(user_key)
                    st.warning("All custom ratings and preferences cleared.")
                    st.rerun()

    # User History Section (for existing users)
    custom_ratings_dict = get_user_ratings(user_key)
    favorite_genres_list = get_preferences(user_key)

    if user_mode.startswith("Existing"):
        user_history = ratings_df[ratings_df["user_id"] == selected_user_id]
        with st.expander(f"📜 View User {selected_user_id} Rating History ({len(user_history)} rated titles)", expanded=False):
            merged_hist = pd.merge(user_history, movies_df[["movie_id", "clean_title", "year", "genres"]], on="movie_id")
            merged_hist = merged_hist.sort_values(by="rating", ascending=False)
            st.dataframe(
                merged_hist[["clean_title", "year", "genres", "rating"]].rename(
                    columns={"clean_title": "Title", "year": "Year", "genres": "Genres", "rating": "Rating (1-5)"}
                ),
                use_container_width=True,
                height=250
            )

    # Recommendation Controls
    st.html("""<hr style="border-color: rgba(255,255,255,0.08); margin: 25px 0 20px 0;">
<h3 style="color: #FFFFFF !important; font-size: 1.35rem; font-weight: 800; margin: 0 0 14px 0;">⚙️ Recommendation Controls</h3>""")

    c_algo, c_topn, c_genre, c_exclude = st.columns([2, 1, 1, 1])
    with c_algo:
        algo_choice = st.selectbox(
            "Recommendation Algorithm:",
            [
                "Adaptive Hybrid Engine (Recommended)",
                "User-Based Collaborative Filtering (UBCF)",
                "Item-Based Collaborative Filtering (IBCF)",
                "Content / Genre-Based Profiling",
                "Popularity (Bayesian Weighted)"
            ]
        )
    with c_topn:
        top_k = st.slider("Top N Results:", min_value=3, max_value=20, value=9, step=1)
    with c_genre:
        all_genres_list = ["All", "Action", "Adventure", "Animation", "Children's", "Comedy", "Crime", "Drama", "Horror", "Romance", "Sci-Fi", "Thriller"]
        genre_filter = st.selectbox("Genre Filter:", all_genres_list)
    with c_exclude:
        st.html("<div style='height: 28px;'></div>")
        exclude_rated = st.checkbox("Exclude Already Rated", value=True)

    # Hybrid weights tuning (if Hybrid chosen)
    w_cf, w_cnt, w_pop = None, None, None
    if "Hybrid" in algo_choice:
        with st.expander("🛠️ Custom Hybrid Weights Tuning (Optional)"):
            cw1, cw2, cw3 = st.columns(3)
            with cw1:
                w_cf_slider = st.slider("Collaborative Weight (w_cf):", 0.0, 1.0, 0.50, 0.05)
            with cw2:
                w_cnt_slider = st.slider("Content / Genre Weight (w_content):", 0.0, 1.0, 0.30, 0.05)
            with cw3:
                w_pop_slider = st.slider("Popularity Weight (w_pop):", 0.0, 1.0, 0.20, 0.05)
            w_cf, w_cnt, w_pop = w_cf_slider, w_cnt_slider, w_pop_slider

    # Generate Recommendations
    with st.spinner("Computing real-time recommendations..."):
        recs = pd.DataFrame()
        if "Hybrid" in algo_choice:
            recs = hybrid_model.recommend(
                user_id=selected_user_id,
                top_n=top_k,
                genre=genre_filter,
                exclude_rated=exclude_rated,
                cf_weight=w_cf,
                content_weight=w_cnt,
                pop_weight=w_pop,
                custom_ratings=custom_ratings_dict,
                favorite_genres=favorite_genres_list
            )
        elif "User-Based" in algo_choice:
            recs = ubcf_model.recommend(
                user_id=selected_user_id,
                top_n=top_k,
                genre=genre_filter,
                exclude_rated=exclude_rated
            )
        elif "Item-Based" in algo_choice:
            recs = ibcf_model.recommend(
                user_id=selected_user_id,
                top_n=top_k,
                genre=genre_filter,
                exclude_rated=exclude_rated
            )
        elif "Content" in algo_choice:
            if selected_user_id == 99999 and not custom_ratings_dict and favorite_genres_list:
                recs = content_model.recommend_by_genres(
                    favorite_genres=favorite_genres_list,
                    top_n=top_k
                )
            else:
                recs = content_model.recommend(
                    user_id=selected_user_id,
                    top_n=top_k,
                    genre=genre_filter,
                    exclude_rated=exclude_rated,
                    custom_ratings=custom_ratings_dict
                )
        elif "Popularity" in algo_choice:
            recs = pop_model.recommend(
                top_n=top_k,
                genre=genre_filter
            )

    # Render Recommendations Cards & CSV Export
    if recs.empty:
        st.warning("⚠️ No recommendations could be generated for the given filters. Try clearing genre filters or rating a few movies!")
    else:
        st.html(f"""<div style="margin: 25px 0 14px 0; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
<h3 style="color: #FFFFFF !important; font-size: 1.45rem; font-weight: 800; margin: 0;">🍿 Recommended Movies for You ({len(recs)} titles)</h3>
</div>""")

        # CSV Export Button
        export_df = recs[["clean_title", "year", "genres", "recommendation_score", "explanation"]].copy()
        csv_data = export_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Export Recommendations to CSV",
            data=csv_data,
            file_name=f"cinematch_recs_user_{selected_user_id}.csv",
            mime="text/csv"
        )
        st.html("<div style='height: 14px;'></div>")

        cols = st.columns(3)
        for idx, (_, row) in enumerate(recs.iterrows()):
            with cols[idx % 3]:
                render_movie_card(row, show_score=True, show_explanation=True, rank=idx + 1)
