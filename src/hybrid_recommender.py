"""
CineMatch AI - Hybrid Recommender Module
Combines Collaborative Filtering, Content-Based, and Popularity signals with cold-start fallback.
"""

from typing import List, Dict, Tuple, Optional, Any
import numpy as np
import pandas as pd

from src.utils import setup_logger
from src.popularity_recommender import PopularityRecommender
from src.collaborative_filtering import UserBasedCF, ItemBasedCF
from src.content_recommender import ContentRecommender

logger = setup_logger("hybrid_recommender")


class HybridRecommender:
    """
    Configurable Hybrid Recommender integrating:
    1. Collaborative Filtering (User-Based or Item-Based)
    2. Content-Based / Genre Filtering
    3. Bayesian Popularity Filtering
    """

    def __init__(
        self,
        cf_type: str = "user",
        weight_cf: float = 0.50,
        weight_content: float = 0.30,
        weight_popularity: float = 0.20
    ):
        self.cf_type = cf_type
        self.weight_cf = weight_cf
        self.weight_content = weight_content
        self.weight_popularity = weight_popularity

        self.popularity_model = PopularityRecommender()
        self.ubcf_model = UserBasedCF()
        self.ibcf_model = ItemBasedCF()
        self.content_model = ContentRecommender()

        self.ratings_df: Optional[pd.DataFrame] = None
        self.movies_df: Optional[pd.DataFrame] = None
        self.is_fitted = False

    def fit(self, ratings: pd.DataFrame, movies: pd.DataFrame) -> "HybridRecommender":
        """
        Fits all underlying recommendation engines.
        """
        logger.info("Fitting HybridRecommender engines...")
        self.ratings_df = ratings.copy()
        self.movies_df = movies.copy()

        self.popularity_model.fit(ratings, movies)
        self.ubcf_model.fit(ratings, movies)
        self.ibcf_model.fit(ratings, movies)
        self.content_model.fit(ratings, movies)

        self.is_fitted = True
        logger.info("HybridRecommender successfully fitted.")
        return self

    def recommend(
        self,
        user_id: int,
        top_n: int = 10,
        genre: Optional[str] = None,
        exclude_rated: bool = True,
        cf_weight: Optional[float] = None,
        content_weight: Optional[float] = None,
        pop_weight: Optional[float] = None,
        custom_ratings: Optional[Dict[int, float]] = None,
        favorite_genres: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Generates hybrid recommendations with automatic cold-start handling and explainability.
        """
        if not self.is_fitted:
            raise ValueError("HybridRecommender not fitted. Call fit() first.")

        # Determine user rating count
        user_ratings_count = 0
        rated_movie_ids = set()

        if self.ratings_df is not None:
            user_ratings = self.ratings_df[self.ratings_df["user_id"] == user_id]
            user_ratings_count = len(user_ratings)
            rated_movie_ids = set(user_ratings["movie_id"].tolist())

        if custom_ratings:
            user_ratings_count += len(custom_ratings)
            rated_movie_ids.update(custom_ratings.keys())

        # Dynamic weights for Cold-Start Mitigation
        if user_ratings_count == 0:
            # Case 1: Pure Cold Start
            logger.info(f"User {user_id} has 0 ratings (Cold-Start). Using Popularity & Genre fallback.")
            if favorite_genres:
                w_cf, w_cnt, w_pop = 0.0, 0.60, 0.40
            else:
                w_cf, w_cnt, w_pop = 0.0, 0.0, 1.0
        elif user_ratings_count < 5:
            # Case 2: Warm-up Sparse Profile
            logger.info(f"User {user_id} has {user_ratings_count} ratings. Increasing Content & Popularity weights.")
            w_cf, w_cnt, w_pop = 0.25, 0.45, 0.30
        else:
            # Case 3: Mature Profile
            w_cf = cf_weight if cf_weight is not None else self.weight_cf
            w_cnt = content_weight if content_weight is not None else self.weight_content
            w_pop = pop_weight if pop_weight is not None else self.weight_popularity

        # Normalize weights
        total_w = w_cf + w_cnt + w_pop
        if total_w > 0:
            w_cf, w_cnt, w_pop = w_cf / total_w, w_cnt / total_w, w_pop / total_w
        else:
            w_pop = 1.0

        # 1. Popularity candidate scores
        pop_df = self.popularity_model.movie_stats.copy()
        if exclude_rated:
            pop_df = pop_df[~pop_df["movie_id"].isin(rated_movie_ids)]
        # Min-max scale popularity weighted_score (range ~ 1.0 to 5.0)
        pop_score_norm = (pop_df["weighted_score"] - 1.0) / 4.0
        pop_map = dict(zip(pop_df["movie_id"], np.clip(pop_score_norm, 0.0, 1.0)))

        # 2. Collaborative candidate scores
        cf_map: Dict[int, float] = {}
        if w_cf > 0 and user_ratings_count > 0:
            cf_model = self.ubcf_model if self.cf_type == "user" else self.ibcf_model
            try:
                cf_recs = cf_model.recommend(
                    user_id=user_id,
                    top_n=top_n * 5,
                    exclude_rated=exclude_rated
                )
                if not cf_recs.empty:
                    # Predicted ratings range 1.0 to 5.0
                    for _, r in cf_recs.iterrows():
                        norm_score = (r["predicted_rating"] - 1.0) / 4.0
                        cf_map[int(r["movie_id"])] = float(np.clip(norm_score, 0.0, 1.0))
            except Exception as e:
                logger.warning(f"Collaborative filtering warning: {e}")

        # 3. Content candidate scores
        cnt_map: Dict[int, float] = {}
        if w_cnt > 0:
            try:
                if user_ratings_count > 0:
                    cnt_recs = self.content_model.recommend(
                        user_id=user_id,
                        top_n=top_n * 5,
                        exclude_rated=exclude_rated,
                        custom_ratings=custom_ratings
                    )
                elif favorite_genres:
                    cnt_recs = self.content_model.recommend_by_genres(
                        favorite_genres=favorite_genres,
                        top_n=top_n * 5,
                        exclude_movie_ids=list(rated_movie_ids)
                    )
                else:
                    cnt_recs = pd.DataFrame()

                if not cnt_recs.empty:
                    for _, r in cnt_recs.iterrows():
                        cnt_map[int(r["movie_id"])] = float(np.clip(r["recommendation_score"], 0.0, 1.0))
            except Exception as e:
                logger.warning(f"Content recommender warning: {e}")

        # Combine candidate IDs
        all_candidate_ids = set(pop_map.keys())
        if cf_map:
            all_candidate_ids.update(cf_map.keys())
        if cnt_map:
            all_candidate_ids.update(cnt_map.keys())

        # Score candidates
        hybrid_scores = []
        for mid in all_candidate_ids:
            s_cf = cf_map.get(mid, 0.0)
            s_cnt = cnt_map.get(mid, 0.0)
            s_pop = pop_map.get(mid, 0.0)

            # Effective score
            score = (w_cf * s_cf) + (w_cnt * s_cnt) + (w_pop * s_pop)
            # Projected rating on 1-5 scale
            projected_rating = 1.0 + (score * 4.0)

            hybrid_scores.append({
                "movie_id": mid,
                "hybrid_score": round(score, 3),
                "predicted_rating": round(projected_rating, 2),
                "s_cf": round(s_cf, 3),
                "s_cnt": round(s_cnt, 3),
                "s_pop": round(s_pop, 3),
            })

        h_df = pd.DataFrame(hybrid_scores).sort_values(by="hybrid_score", ascending=False)
        merged = pd.merge(h_df, self.movies_df, on="movie_id", how="left")

        # Genre filter
        if genre and genre != "All":
            if genre in merged.columns:
                merged = merged[merged[genre] == 1]
            else:
                merged = merged[merged["genres"].str.contains(genre, case=False, na=False)]

        results = merged.head(top_n).copy()

        # Dynamic, honest explanations
        explanations = []
        for _, row in results.iterrows():
            if user_ratings_count == 0:
                if favorite_genres and any(g in row["genres"] for g in favorite_genres):
                    exp = f"Recommended based on your preferred genre ({row['genres'].replace('|', ', ')})."
                else:
                    exp = "Top community favorite with high ratings across all users."
            else:
                # Compare weighted signals
                cf_contrib = w_cf * row["s_cf"]
                cnt_contrib = w_cnt * row["s_cnt"]
                pop_contrib = w_pop * row["s_pop"]

                if cf_contrib >= max(cnt_contrib, pop_contrib) and row["s_cf"] > 0.4:
                    exp = f"Users with similar taste to yours rated this highly ({row['predicted_rating']:.1f}/5)."
                elif cnt_contrib >= max(cf_contrib, pop_contrib) and row["s_cnt"] > 0.4:
                    exp = f"Matches your preferred cinematic themes in {row['genres'].replace('|', ', ')}."
                else:
                    exp = f"Hybrid pick: High community rating & strong synergy with your profile."
            explanations.append(exp)

        results["explanation"] = explanations
        results["recommendation_score"] = results["predicted_rating"]
        return results
