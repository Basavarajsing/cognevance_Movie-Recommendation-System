"""
CineMatch AI - Intelligent Movie Recommendation System
Main Streamlit Application Entrypoint
"""

import streamlit as st
import pandas as pd
from pathlib import Path

from app.styles import CUSTOM_CSS
from app.home import render_home_page
from app.recommendations import render_recommendations_page
from app.explore import render_explore_page
from app.genre_explorer import render_genre_explorer_page
from app.analytics import render_analytics_page
from app.model_performance import render_model_performance_page
from app.about import render_about_page

from src.preprocessing import load_processed_data
from src.popularity_recommender import PopularityRecommender
from src.collaborative_filtering import UserBasedCF, ItemBasedCF
from src.content_recommender import ContentRecommender
from src.hybrid_recommender import HybridRecommender
from src.db import init_db

# Configure Streamlit Page
st.set_page_config(
    page_title="CineMatch AI – Intelligent Movie Recommendation System",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Custom Cinematic Dark Styles
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


@st.cache_data(show_spinner="Loading and validating MovieLens dataset...")
def get_dataset():
    """Cached loader for processed datasets."""
    ratings, movies, users = load_processed_data()
    return ratings, movies, users


@st.cache_resource(show_spinner="Initializing and fitting machine learning recommender engines...")
def get_models(ratings_df, movies_df):
    """Cached loader for recommendation models."""
    pop = PopularityRecommender(min_votes_threshold=25).fit(ratings_df, movies_df)
    ubcf = UserBasedCF(k_neighbors=25).fit(ratings_df, movies_df)
    ibcf = ItemBasedCF(k_neighbors=20).fit(ratings_df, movies_df)
    content = ContentRecommender().fit(ratings_df, movies_df)
    hybrid = HybridRecommender(cf_type="user", weight_cf=0.50, weight_content=0.30, weight_popularity=0.20)
    hybrid.fit(ratings_df, movies_df)
    return pop, ubcf, ibcf, content, hybrid


def main():
    # Initialize SQLite database
    init_db()

    # Load Data & Models
    ratings_df, movies_df, users_df = get_dataset()
    pop_model, ubcf_model, ibcf_model, content_model, hybrid_model = get_models(ratings_df, movies_df)

    # Sidebar Navigation
    st.sidebar.html("""<div style="text-align: center; padding: 12px 0 16px 0;">
<div style="display: inline-block; background: linear-gradient(135deg, #6366F1, #8B5CF6); border-radius: 12px; padding: 8px 12px; margin-bottom: 8px;">
<span style="font-size: 24px;">🎬</span>
</div>
<h2 style="margin: 0; font-size: 1.4rem; font-weight: 800; background: linear-gradient(135deg, #FFF, #C4B5FD); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
CineMatch AI
</h2>
<span style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 1px;">
Intelligent Recommender
</span>
</div>""")

    page = st.sidebar.radio(
        "Navigation Menu:",
        [
            "🏠 Home Dashboard",
            "🎯 Personalized Recs",
            "🔍 Explore Movies",
            "🎭 Genre Explorer",
            "📊 Analytics & EDA",
            "📈 Model Performance",
            "ℹ️ About Project"
        ]
    )

    st.sidebar.html("""<hr style="border-color: rgba(255,255,255,0.08); margin: 15px 0;">
<div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 12px; font-size: 0.8rem; color: #94A3B8;">
<div style="color: #10B981; font-weight: 700; margin-bottom: 4px;">● System Status: Online</div>
<div>• Dataset: MovieLens 100K</div>
<div>• Movies: 1,682</div>
<div>• Users: 943</div>
<div>• Engine: Hybrid (CF+Content+Pop)</div>
</div>""")

    # Page Routing
    if page == "🏠 Home Dashboard":
        render_home_page(ratings_df, movies_df, pop_model)
    elif page == "🎯 Personalized Recs":
        render_recommendations_page(
            ratings_df, movies_df, hybrid_model, pop_model, ubcf_model, ibcf_model, content_model
        )
    elif page == "🔍 Explore Movies":
        render_explore_page(movies_df, ratings_df, ibcf_model, content_model)
    elif page == "🎭 Genre Explorer":
        render_genre_explorer_page(movies_df, ratings_df, pop_model)
    elif page == "📊 Analytics & EDA":
        render_analytics_page(ratings_df, movies_df, users_df)
    elif page == "📈 Model Performance":
        render_model_performance_page()
    elif page == "ℹ️ About Project":
        render_about_page()


if __name__ == "__main__":
    main()
