"""
CineMatch AI - Popularity-Based Recommender Module
Implements Bayesian weighted rating (IMDB formula) and popularity ranking.
"""

from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np

from src.utils import setup_logger

logger = setup_logger("popularity_recommender")


class PopularityRecommender:
    """
    Popularity and Bayesian Weighted Recommender.
    Formula:
        WR = (v / (v + m)) * R + (m / (v + m)) * C
    where:
        v = number of votes/ratings for the movie
        m = minimum votes required to be listed (configurable threshold)
        R = average rating of the movie
        C = mean vote across the whole dataset
    """

    def __init__(self, min_votes_threshold: int = 30):
        self.min_votes_threshold = min_votes_threshold
        self.movie_stats: Optional[pd.DataFrame] = None
        self.global_mean_rating: float = 0.0

    def fit(self, ratings: pd.DataFrame, movies: pd.DataFrame) -> "PopularityRecommender":
        """
        Computes rating counts, average ratings, and Bayesian weighted ratings.
        """
        logger.info("Fitting PopularityRecommender...")
        self.global_mean_rating = float(ratings["rating"].mean())
        C = self.global_mean_rating
        m = self.min_votes_threshold

        stats = ratings.groupby("movie_id").agg(
            vote_count=("rating", "count"),
            avg_rating=("rating", "mean")
        ).reset_index()

        # Merge with movies metadata
        merged = pd.merge(movies, stats, on="movie_id", how="left")
        merged["vote_count"] = merged["vote_count"].fillna(0).astype(int)
        merged["avg_rating"] = merged["avg_rating"].fillna(0.0).round(2)

        # Compute Bayesian Weighted Rating
        v = merged["vote_count"]
        R = merged["avg_rating"]
        merged["weighted_score"] = (v / (v + m)) * R + (m / (v + m)) * C
        merged["weighted_score"] = merged["weighted_score"].round(3)

        self.movie_stats = merged.sort_values(by="weighted_score", ascending=False).reset_index(drop=True)
        logger.info(f"PopularityRecommender fitted on {len(self.movie_stats)} movies. Global mean C={C:.2f}")
        return self

    def recommend(
        self,
        top_n: int = 10,
        genre: Optional[str] = None,
        min_votes: Optional[int] = None,
        exclude_movie_ids: Optional[List[int]] = None
    ) -> pd.DataFrame:
        """
        Recommends top N movies sorted by weighted score.
        Optional filtering by genre, minimum votes, and exclusion of already-seen movie IDs.
        """
        if self.movie_stats is None:
            raise ValueError("Recommender has not been fitted. Call fit() first.")

        df = self.movie_stats.copy()

        # Exclude specified movies
        if exclude_movie_ids:
            df = df[~df["movie_id"].isin(exclude_movie_ids)]

        # Filter by minimum votes if specified
        threshold = min_votes if min_votes is not None else self.min_votes_threshold
        df = df[df["vote_count"] >= threshold]

        # Filter by genre if specified
        if genre and genre != "All":
            if genre in df.columns:
                df = df[df[genre] == 1]
            else:
                df = df[df["genres"].str.contains(genre, case=False, na=False)]

        results = df.head(top_n).copy()

        # Add readable explanations
        explanations = []
        for rank, (_, row) in enumerate(results.iterrows(), start=1):
            exp = (
                f"Highly rated by community (#{rank}): "
                f"{row['avg_rating']:.1f}/5 from {int(row['vote_count']):,} reviews."
            )
            explanations.append(exp)

        results["explanation"] = explanations
        results["recommendation_score"] = results["weighted_score"]
        return results

    def get_most_rated(self, top_n: int = 10) -> pd.DataFrame:
        """Returns top N movies with the highest number of ratings."""
        if self.movie_stats is None:
            raise ValueError("Recommender has not been fitted. Call fit() first.")
        return self.movie_stats.sort_values(by="vote_count", ascending=False).head(top_n)

    def get_highest_rated(self, top_n: int = 10, min_votes: int = 50) -> pd.DataFrame:
        """Returns top N highest rated movies with a vote count >= min_votes."""
        if self.movie_stats is None:
            raise ValueError("Recommender has not been fitted. Call fit() first.")
        filtered = self.movie_stats[self.movie_stats["vote_count"] >= min_votes]
        return filtered.sort_values(by="avg_rating", ascending=False).head(top_n)
