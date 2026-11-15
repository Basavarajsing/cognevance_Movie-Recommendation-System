"""
Unit tests for all recommendation algorithms, hybrid engine, cold-start handling, and SQLite database.
"""

import pytest
import pandas as pd
import numpy as np

from src.preprocessing import load_processed_data
from src.popularity_recommender import PopularityRecommender
from src.collaborative_filtering import UserBasedCF, ItemBasedCF
from src.content_recommender import ContentRecommender
from src.hybrid_recommender import HybridRecommender
from src.db import save_rating, get_user_ratings, save_preferences, get_preferences, reset_user_data, toggle_bookmark, get_bookmarks


@pytest.fixture(scope="module")
def data():
    ratings, movies, users = load_processed_data()
    return ratings, movies, users


def test_popularity_recommender(data):
    ratings, movies, _ = data
    pop = PopularityRecommender(min_votes_threshold=20)
    pop.fit(ratings, movies)

    assert pop.movie_stats is not None
    assert "weighted_score" in pop.movie_stats.columns
    assert pop.global_mean_rating > 3.0 and pop.global_mean_rating < 4.0

    recs = pop.recommend(top_n=5)
    assert len(recs) == 5
    assert (recs["recommendation_score"].diff().dropna() <= 0.001).all()

    # Test genre filter
    action_recs = pop.recommend(top_n=5, genre="Action")
    assert len(action_recs) == 5
    assert (action_recs["Action"] == 1).all()


def test_user_based_cf(data):
    ratings, movies, _ = data
    ubcf = UserBasedCF(k_neighbors=15)
    ubcf.fit(ratings, movies)

    pred = ubcf.predict_rating(user_id=1, movie_id=50)
    assert 1.0 <= pred <= 5.0

    recs = ubcf.recommend(user_id=1, top_n=5)
    assert len(recs) == 5
    assert "explanation" in recs.columns
    assert (recs["recommendation_score"] >= 1.0).all()


def test_item_based_cf(data):
    ratings, movies, _ = data
    ibcf = ItemBasedCF(k_neighbors=15)
    ibcf.fit(ratings, movies)

    # Test item similarities
    sim_movies = ibcf.get_similar_items(movie_id=1, top_n=5)
    assert len(sim_movies) == 5
    assert "similarity" in sim_movies.columns

    pred = ibcf.predict_rating(user_id=1, movie_id=50)
    assert 1.0 <= pred <= 5.0

    recs = ibcf.recommend(user_id=1, top_n=5)
    assert not recs.empty
    assert "explanation" in recs.columns


def test_content_recommender(data):
    ratings, movies, _ = data
    content = ContentRecommender()
    content.fit(ratings, movies)

    sims = content.get_similar_movies(movie_id=1, top_n=5)
    assert len(sims) == 5
    assert "similarity" in sims.columns

    # Test cold start with favorite genres
    genre_recs = content.recommend_by_genres(["Animation", "Comedy"], top_n=5)
    assert len(genre_recs) == 5
    assert "genre_score" in genre_recs.columns


def test_hybrid_recommender_and_cold_start(data):
    ratings, movies, _ = data
    hybrid = HybridRecommender(cf_type="user", weight_cf=0.5, weight_content=0.3, weight_popularity=0.2)
    hybrid.fit(ratings, movies)

    # Mature user
    recs = hybrid.recommend(user_id=1, top_n=5)
    assert len(recs) == 5
    assert "predicted_rating" in recs.columns
    assert "explanation" in recs.columns

    # Cold start user with ID 99999 (does not exist in ratings)
    cold_recs = hybrid.recommend(user_id=99999, top_n=5, favorite_genres=["Sci-Fi", "Action"])
    assert len(cold_recs) == 5
    assert "explanation" in cold_recs.columns
    assert any("preferred genre" in exp.lower() or "community" in exp.lower() for exp in cold_recs["explanation"])


def test_sqlite_database_persistence():
    test_user = "test_user_pytest_999"
    reset_user_data(test_user)

    # Save ratings
    save_rating(test_user, 1, 5.0)
    save_rating(test_user, 50, 4.5)
    user_ratings = get_user_ratings(test_user)
    assert user_ratings[1] == 5.0
    assert user_ratings[50] == 4.5

    # Save preferences
    save_preferences(test_user, ["Animation", "Sci-Fi"])
    prefs = get_preferences(test_user)
    assert "Animation" in prefs
    assert "Sci-Fi" in prefs

    # Bookmarks
    assert toggle_bookmark(test_user, 100) is True
    assert 100 in get_bookmarks(test_user)
    assert toggle_bookmark(test_user, 100) is False
    assert 100 not in get_bookmarks(test_user)

    reset_user_data(test_user)
    assert len(get_user_ratings(test_user)) == 0
