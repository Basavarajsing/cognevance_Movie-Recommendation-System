"""
CineMatch AI - Collaborative Filtering Recommender Module
Implements User-Based Collaborative Filtering (UBCF) and Item-Based Collaborative Filtering (IBCF).
"""

from typing import List, Dict, Tuple, Optional, Any
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import joblib

from src.utils import setup_logger, get_paths

logger = setup_logger("collaborative_filtering")


class UserBasedCF:
    """
    User-Based Collaborative Filtering using mean-centered cosine similarity.
    """

    def __init__(self, k_neighbors: int = 30, min_similarity: float = 0.05):
        self.k_neighbors = k_neighbors
        self.min_similarity = min_similarity
        self.user_item_matrix: Optional[pd.DataFrame] = None
        self.user_mean: Optional[pd.Series] = None
        self.user_similarity_df: Optional[pd.DataFrame] = None
        self.movies_df: Optional[pd.DataFrame] = None
        self.global_mean: float = 3.53

    def fit(self, ratings: pd.DataFrame, movies: pd.DataFrame) -> "UserBasedCF":
        """
        Builds user-item matrix, computes mean ratings and user-user cosine similarities.
        """
        logger.info("Fitting User-Based Collaborative Filtering...")
        self.movies_df = movies.copy()
        self.global_mean = float(ratings["rating"].mean())

        # Pivot user-item rating matrix
        self.user_item_matrix = ratings.pivot(
            index="user_id", columns="movie_id", values="rating"
        )

        # Compute user mean ratings
        self.user_mean = self.user_item_matrix.mean(axis=1)

        # Mean-center the rating matrix for users (fill NaNs with 0 for centered ratings)
        centered_matrix = self.user_item_matrix.sub(self.user_mean, axis=0).fillna(0)

        # Compute cosine similarity between users
        sim_matrix = cosine_similarity(centered_matrix.values)
        user_ids = self.user_item_matrix.index
        self.user_similarity_df = pd.DataFrame(
            sim_matrix, index=user_ids, columns=user_ids
        )

        logger.info(
            f"UserBasedCF fitted: {len(user_ids)} users x {self.user_item_matrix.shape[1]} movies."
        )
        return self

    def predict_rating(self, user_id: int, movie_id: int) -> float:
        """
        Predict rating for user_id on movie_id using top-K similar users.
        """
        if self.user_item_matrix is None or self.user_similarity_df is None:
            raise ValueError("Model not fitted. Call fit() first.")

        if user_id not in self.user_item_matrix.index:
            # Cold-start user
            return self.global_mean

        if movie_id not in self.user_item_matrix.columns:
            # Cold-start movie
            return float(self.user_mean.get(user_id, self.global_mean))

        # Check if user already rated it
        existing_rating = self.user_item_matrix.loc[user_id, movie_id]
        if pd.notnull(existing_rating):
            return float(existing_rating)

        # Other users who rated this movie
        other_ratings = self.user_item_matrix[movie_id].dropna()
        if other_ratings.empty:
            return float(self.user_mean.get(user_id, self.global_mean))

        # Similarities with other users who rated this movie
        sims = self.user_similarity_df.loc[user_id, other_ratings.index]
        # Keep positive correlations above min_similarity
        valid_mask = sims > self.min_similarity
        sims = sims[valid_mask]
        other_ratings = other_ratings[valid_mask]

        if sims.empty:
            return float(self.user_mean.get(user_id, self.global_mean))

        # Top K neighbors
        if len(sims) > self.k_neighbors:
            top_indices = sims.nlargest(self.k_neighbors).index
            sims = sims[top_indices]
            other_ratings = other_ratings[top_indices]

        other_means = self.user_mean[other_ratings.index]
        centered_ratings = other_ratings - other_means

        sim_sum = sims.abs().sum()
        if sim_sum == 0:
            return float(self.user_mean.get(user_id, self.global_mean))

        u_mean = float(self.user_mean[user_id])
        predicted = u_mean + (sims.values @ centered_ratings.values) / sim_sum
        return float(np.clip(predicted, 1.0, 5.0))

    def recommend(
        self,
        user_id: int,
        top_n: int = 10,
        genre: Optional[str] = None,
        exclude_rated: bool = True
    ) -> pd.DataFrame:
        """
        Recommends top N unseen movies for a given user.
        """
        if self.user_item_matrix is None:
            raise ValueError("Model not fitted. Call fit() first.")

        if user_id not in self.user_item_matrix.index:
            # Fallback for cold start
            logger.info(f"User {user_id} not in training set. Returning empty for CF.")
            return pd.DataFrame()

        user_ratings = self.user_item_matrix.loc[user_id]
        rated_movie_ids = set(user_ratings.dropna().index) if exclude_rated else set()

        # Find top similar users
        user_sims = self.user_similarity_df.loc[user_id].drop(user_id)
        pos_sims = user_sims[user_sims > self.min_similarity].nlargest(self.k_neighbors)

        if pos_sims.empty:
            return pd.DataFrame()

        # Candidates are movies rated by these neighbors
        neighbor_ratings = self.user_item_matrix.loc[pos_sims.index]
        candidate_movies = neighbor_ratings.columns[neighbor_ratings.notnull().any()]
        candidate_movies = [m for m in candidate_movies if m not in rated_movie_ids]

        predictions = []
        for m_id in candidate_movies:
            pred = self.predict_rating(user_id, m_id)
            predictions.append((m_id, pred))

        if not predictions:
            return pd.DataFrame()

        pred_df = pd.DataFrame(predictions, columns=["movie_id", "predicted_rating"])
        pred_df = pred_df.sort_values(by="predicted_rating", ascending=False)

        # Merge with movies
        merged = pd.merge(pred_df, self.movies_df, on="movie_id", how="left")

        # Genre filter
        if genre and genre != "All":
            if genre in merged.columns:
                merged = merged[merged[genre] == 1]
            else:
                merged = merged[merged["genres"].str.contains(genre, case=False, na=False)]

        results = merged.head(top_n).copy()
        avg_top_sim = float(pos_sims.mean())

        explanations = []
        for _, row in results.iterrows():
            exp = (
                f"Users with similar taste ({avg_top_sim * 100:.0f}% taste match) "
                f"predicted you'll rate this {row['predicted_rating']:.2f}/5."
            )
            explanations.append(exp)

        results["explanation"] = explanations
        results["recommendation_score"] = results["predicted_rating"].round(2)
        return results


class ItemBasedCF:
    """
    Item-Based Collaborative Filtering using adjusted cosine similarity.
    """

    def __init__(self, k_neighbors: int = 25, min_similarity: float = 0.05):
        self.k_neighbors = k_neighbors
        self.min_similarity = min_similarity
        self.item_user_matrix: Optional[pd.DataFrame] = None
        self.item_similarity_df: Optional[pd.DataFrame] = None
        self.item_mean: Optional[pd.Series] = None
        self.movies_df: Optional[pd.DataFrame] = None
        self.global_mean: float = 3.53

    def fit(self, ratings: pd.DataFrame, movies: pd.DataFrame) -> "ItemBasedCF":
        """
        Builds item-user matrix and computes item-item cosine similarity.
        """
        logger.info("Fitting Item-Based Collaborative Filtering...")
        self.movies_df = movies.copy()
        self.global_mean = float(ratings["rating"].mean())

        # Pivot item-user matrix (rows: movie_id, cols: user_id)
        self.item_user_matrix = ratings.pivot(
            index="movie_id", columns="user_id", values="rating"
        )
        self.item_mean = self.item_user_matrix.mean(axis=1)

        # Adjusted cosine: subtract user mean across items
        user_mean = ratings.groupby("user_id")["rating"].mean()
        centered_ratings = ratings.copy()
        centered_ratings["centered"] = centered_ratings["rating"] - centered_ratings["user_id"].map(user_mean)

        centered_pivot = centered_ratings.pivot(
            index="movie_id", columns="user_id", values="centered"
        ).fillna(0)

        # Compute cosine similarity between movies
        sim_matrix = cosine_similarity(centered_pivot.values)
        movie_ids = centered_pivot.index
        self.item_similarity_df = pd.DataFrame(
            sim_matrix, index=movie_ids, columns=movie_ids
        )

        logger.info(
            f"ItemBasedCF fitted: {len(movie_ids)} movies x {self.item_user_matrix.shape[1]} users."
        )
        return self

    def get_similar_items(self, movie_id: int, top_n: int = 10) -> pd.DataFrame:
        """
        Returns top N most similar movies to the given movie_id.
        """
        if self.item_similarity_df is None or movie_id not in self.item_similarity_df.index:
            return pd.DataFrame()

        sims = self.item_similarity_df.loc[movie_id].drop(movie_id)
        top_sims = sims[sims > self.min_similarity].nlargest(top_n)

        if top_sims.empty:
            return pd.DataFrame()

        sim_df = pd.DataFrame({
            "movie_id": top_sims.index,
            "similarity": top_sims.values.round(3)
        })

        merged = pd.merge(sim_df, self.movies_df, on="movie_id", how="left")
        source_title = self.movies_df.loc[self.movies_df["movie_id"] == movie_id, "title"].values
        src_name = source_title[0] if len(source_title) > 0 else f"Movie {movie_id}"

        explanations = [
            f"Similar rating patterns to '{src_name}' ({sim * 100:.0f}% pattern match)."
            for sim in merged["similarity"]
        ]
        merged["explanation"] = explanations
        merged["recommendation_score"] = merged["similarity"]
        return merged

    def predict_rating(self, user_id: int, movie_id: int) -> float:
        """
        Predicts rating of user_id for movie_id based on user's past ratings of similar items.
        """
        if self.item_user_matrix is None or self.item_similarity_df is None:
            raise ValueError("Model not fitted. Call fit() first.")

        if movie_id not in self.item_similarity_df.index:
            return self.global_mean

        if user_id not in self.item_user_matrix.columns:
            return float(self.item_mean.get(movie_id, self.global_mean))

        # Check existing rating
        existing = self.item_user_matrix.loc[movie_id, user_id]
        if pd.notnull(existing):
            return float(existing)

        # Movies rated by this user
        user_ratings = self.item_user_matrix[user_id].dropna()
        if user_ratings.empty:
            return float(self.item_mean.get(movie_id, self.global_mean))

        # Similarities of target movie with movies user rated
        sims = self.item_similarity_df.loc[movie_id, user_ratings.index]
        valid_mask = sims > self.min_similarity
        sims = sims[valid_mask]
        user_ratings = user_ratings[valid_mask]

        if sims.empty:
            return float(self.item_mean.get(movie_id, self.global_mean))

        if len(sims) > self.k_neighbors:
            top_k = sims.nlargest(self.k_neighbors).index
            sims = sims[top_k]
            user_ratings = user_ratings[top_k]

        sim_sum = sims.abs().sum()
        if sim_sum == 0:
            return float(self.item_mean.get(movie_id, self.global_mean))

        predicted = (sims.values @ user_ratings.values) / sim_sum
        return float(np.clip(predicted, 1.0, 5.0))

    def recommend(
        self,
        user_id: int,
        top_n: int = 10,
        genre: Optional[str] = None,
        exclude_rated: bool = True
    ) -> pd.DataFrame:
        """
        Recommends top N unseen movies based on item similarities to highly-rated movies by the user.
        """
        if self.item_user_matrix is None:
            raise ValueError("Model not fitted. Call fit() first.")

        if user_id not in self.item_user_matrix.columns:
            return pd.DataFrame()

        user_ratings = self.item_user_matrix[user_id].dropna()
        if user_ratings.empty:
            return pd.DataFrame()

        rated_movie_ids = set(user_ratings.index) if exclude_rated else set()

        # Find items most similar to user's favorite rated items (rated >= 3.5)
        high_rated = user_ratings[user_ratings >= 3.5]
        if high_rated.empty:
            high_rated = user_ratings

        candidate_scores: Dict[int, List[float]] = {}
        candidate_anchors: Dict[int, Tuple[int, float, float]] = {}

        for m_id, r in high_rated.items():
            if m_id not in self.item_similarity_df.index:
                continue
            sims = self.item_similarity_df.loc[m_id].drop(m_id)
            top_similar = sims[sims > self.min_similarity].nlargest(self.k_neighbors)

            for sim_mid, sim_val in top_similar.items():
                if sim_mid in rated_movie_ids:
                    continue
                score = sim_val * r
                if sim_mid not in candidate_scores:
                    candidate_scores[sim_mid] = []
                candidate_scores[sim_mid].append(score)

                if sim_mid not in candidate_anchors or sim_val > candidate_anchors[sim_mid][2]:
                    candidate_anchors[sim_mid] = (m_id, r, sim_val)

        if not candidate_scores:
            return pd.DataFrame()

        # Aggregate candidate scores (average score)
        agg_scores = [
            (mid, float(np.mean(scores)), candidate_anchors[mid])
            for mid, scores in candidate_scores.items()
        ]
        agg_df = pd.DataFrame(
            [{"movie_id": mid, "ibcf_score": score, "anchor": anchor} for mid, score, anchor in agg_scores]
        )
        agg_df = agg_df.sort_values(by="ibcf_score", ascending=False)

        merged = pd.merge(agg_df, self.movies_df, on="movie_id", how="left")

        if genre and genre != "All":
            if genre in merged.columns:
                merged = merged[merged[genre] == 1]
            else:
                merged = merged[merged["genres"].str.contains(genre, case=False, na=False)]

        results = merged.head(top_n).copy()

        explanations = []
        for _, row in results.iterrows():
            anchor_mid, anchor_r, sim_val = row["anchor"]
            anchor_title_series = self.movies_df.loc[self.movies_df["movie_id"] == anchor_mid, "title"]
            anchor_title = anchor_title_series.values[0] if len(anchor_title_series) > 0 else f"Movie {anchor_mid}"
            exp = (
                f"Similar to '{anchor_title}' which you rated {anchor_r:.1f}/5 "
                f"({sim_val * 100:.0f}% rating correlation)."
            )
            explanations.append(exp)

        results["explanation"] = explanations
        results["predicted_rating"] = results["ibcf_score"].round(2)
        results["recommendation_score"] = results["ibcf_score"].round(2)
        return results.drop(columns=["anchor"])
