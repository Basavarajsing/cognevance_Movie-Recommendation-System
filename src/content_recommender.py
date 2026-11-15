"""
CineMatch AI - Content/Genre-Based Recommender Module
Builds TF-IDF & Multi-hot Genre feature vectors and calculates content similarity.
"""

from typing import List, Dict, Tuple, Optional, Any
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize

from src.utils import setup_logger
from src.data_loader import GENRE_COLUMNS

logger = setup_logger("content_recommender")


class ContentRecommender:
    """
    Content-Based Filtering using genre multi-hot encoding, release decade,
    and TF-IDF title vectorization.
    """

    def __init__(self):
        self.movies_df: Optional[pd.DataFrame] = None
        self.movie_features: Optional[np.ndarray] = None
        self.movie_similarity_matrix: Optional[np.ndarray] = None
        self.movie_id_to_idx: Dict[int, int] = {}
        self.idx_to_movie_id: Dict[int, int] = {}
        self.user_ratings_df: Optional[pd.DataFrame] = None
        self.active_genres: List[str] = [g for g in GENRE_COLUMNS if g != "unknown"]

    def fit(self, ratings: pd.DataFrame, movies: pd.DataFrame) -> "ContentRecommender":
        """
        Builds feature representations and computes content similarity matrices.
        """
        logger.info("Fitting ContentRecommender...")
        self.movies_df = movies.copy().reset_index(drop=True)
        self.user_ratings_df = ratings.copy()

        self.movie_id_to_idx = {mid: idx for idx, mid in enumerate(self.movies_df["movie_id"])}
        self.idx_to_movie_id = {idx: mid for idx, mid in enumerate(self.movies_df["movie_id"])}

        # 1. Multi-hot genre matrix
        genre_sub = self.movies_df[self.active_genres].values.astype(float)

        # 2. TF-IDF on genres string and title
        corpus = self.movies_df["clean_title"] + " " + self.movies_df["genres"].str.replace("|", " ")
        tfidf = TfidfVectorizer(stop_words="english", max_features=100)
        tfidf_mat = tfidf.fit_transform(corpus).toarray()

        # 3. Concatenate and normalize feature vectors
        combined_features = np.hstack([genre_sub * 2.0, tfidf_mat])
        self.movie_features = normalize(combined_features, axis=1)

        # 4. Precompute content cosine similarity
        self.movie_similarity_matrix = cosine_similarity(self.movie_features)
        logger.info(f"ContentRecommender fitted on {len(self.movies_df)} movies.")
        return self

    def get_similar_movies(self, movie_id: int, top_n: int = 10) -> pd.DataFrame:
        """
        Returns top N movies most similar in genre, theme, and title content.
        """
        if self.movie_similarity_matrix is None or movie_id not in self.movie_id_to_idx:
            return pd.DataFrame()

        idx = self.movie_id_to_idx[movie_id]
        sim_scores = self.movie_similarity_matrix[idx].copy()
        sim_scores[idx] = -1.0  # Exclude self

        top_indices = np.argsort(sim_scores)[::-1][:top_n]
        top_scores = sim_scores[top_indices]

        results = self.movies_df.iloc[top_indices].copy()
        results["similarity"] = top_scores.round(3)
        results["recommendation_score"] = results["similarity"]

        source_row = self.movies_df.iloc[idx]
        src_title = source_row["title"]
        src_genres = set(source_row["genres"].split("|"))

        explanations = []
        for _, row in results.iterrows():
            target_genres = set(row["genres"].split("|"))
            overlap = src_genres.intersection(target_genres)
            overlap_str = ", ".join(overlap) if overlap else "themes"
            exp = (
                f"Shared genre & theme ({overlap_str}) with '{src_title}' "
                f"({row['similarity'] * 100:.0f}% match)."
            )
            explanations.append(exp)

        results["explanation"] = explanations
        return results

    def recommend(
        self,
        user_id: int,
        top_n: int = 10,
        genre: Optional[str] = None,
        exclude_rated: bool = True,
        custom_ratings: Optional[Dict[int, float]] = None
    ) -> pd.DataFrame:
        """
        Builds user preference profile vector and recommends highest-scoring movies.
        """
        if self.movie_features is None:
            raise ValueError("Model not fitted. Call fit() first.")

        # Gather user's ratings
        user_ratings_dict: Dict[int, float] = {}
        if self.user_ratings_df is not None:
            user_slice = self.user_ratings_df[self.user_ratings_df["user_id"] == user_id]
            for _, r in user_slice.iterrows():
                user_ratings_dict[int(r["movie_id"])] = float(r["rating"])

        if custom_ratings:
            user_ratings_dict.update(custom_ratings)

        if not user_ratings_dict:
            return pd.DataFrame()

        rated_mids = set(user_ratings_dict.keys())

        # Construct user profile vector: weighted sum of item features
        user_profile = np.zeros(self.movie_features.shape[1])
        weight_sum = 0.0

        for mid, rating in user_ratings_dict.items():
            if mid in self.movie_id_to_idx and rating >= 3.0:
                idx = self.movie_id_to_idx[mid]
                # Center around 3.0
                weight = rating - 2.5
                user_profile += weight * self.movie_features[idx]
                weight_sum += weight

        if weight_sum > 0:
            user_profile = user_profile / weight_sum
            user_profile = normalize(user_profile.reshape(1, -1))[0]
        else:
            return pd.DataFrame()

        # Compute cosine similarity between user profile and all movies
        scores = self.movie_features @ user_profile

        # Create candidate dataframe
        cand_df = self.movies_df.copy()
        cand_df["content_score"] = scores.round(3)

        if exclude_rated:
            cand_df = cand_df[~cand_df["movie_id"].isin(rated_mids)]

        if genre and genre != "All":
            if genre in cand_df.columns:
                cand_df = cand_df[cand_df[genre] == 1]
            else:
                cand_df = cand_df[cand_df["genres"].str.contains(genre, case=False, na=False)]

        results = cand_df.sort_values(by="content_score", ascending=False).head(top_n).copy()

        explanations = []
        for _, row in results.iterrows():
            exp = (
                f"Matches your taste profile in {row['genres'].replace('|', ', ')} "
                f"({row['content_score'] * 100:.0f}% content affinity)."
            )
            explanations.append(exp)

        results["explanation"] = explanations
        results["recommendation_score"] = results["content_score"]
        return results

    def recommend_by_genres(
        self,
        favorite_genres: List[str],
        top_n: int = 10,
        exclude_movie_ids: Optional[List[int]] = None
    ) -> pd.DataFrame:
        """
        Cold-start recommendation for users with no ratings who selected favorite genres.
        """
        if not favorite_genres or self.movie_features is None:
            return pd.DataFrame()

        # Build synthetic profile from genre indicators
        genre_vec = np.zeros(len(self.active_genres))
        for g in favorite_genres:
            if g in self.active_genres:
                genre_vec[self.active_genres.index(g)] = 1.0

        if genre_vec.sum() == 0:
            return pd.DataFrame()

        # Project into combined feature space
        synth_profile = np.zeros(self.movie_features.shape[1])
        synth_profile[:len(self.active_genres)] = genre_vec * 2.0
        synth_profile = normalize(synth_profile.reshape(1, -1))[0]

        scores = self.movie_features @ synth_profile
        df = self.movies_df.copy()
        df["genre_score"] = scores.round(3)

        if exclude_movie_ids:
            df = df[~df["movie_id"].isin(exclude_movie_ids)]

        results = df.sort_values(by="genre_score", ascending=False).head(top_n).copy()
        explanations = [
            f"Curated for your selected favorite genres ({', '.join(favorite_genres)})."
            for _ in range(len(results))
        ]
        results["explanation"] = explanations
        results["recommendation_score"] = results["genre_score"]
        return results
