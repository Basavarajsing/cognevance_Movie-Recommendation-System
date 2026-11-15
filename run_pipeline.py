"""
CineMatch AI - Master Pipeline Automation Script
Executes full end-to-end pipeline:
1. Preprocessing and dataset validation
2. 10 Comprehensive EDA publication charts
3. Model training & leakage-free evaluation
4. Benchmark recommendation exports (CSV)
5. Compiles executive PDF Project Report
"""

import sys
import time
from pathlib import Path
import pandas as pd

from src.utils import get_paths, setup_logger, ensure_directories, Timer
from src.preprocessing import run_preprocessing, load_processed_data
from src.eda import generate_all_charts
from src.evaluation import run_full_evaluation
from src.hybrid_recommender import HybridRecommender
from src.popularity_recommender import PopularityRecommender
from src.report_generator import generate_pdf_report

logger = setup_logger("master_pipeline")


def main():
    logger.info("=" * 70)
    logger.info(">>> CINEMATCH AI - MASTER REPRODUCIBILITY PIPELINE")
    logger.info("=" * 70)

    paths = get_paths()
    ensure_directories()
    recs_dir = paths["recommendations"]

    with Timer("Step 1: Dataset Validation & Preprocessing"):
        summary = run_preprocessing()
        logger.info(f"Processed counts: {summary['processed_counts']}")

    with Timer("Step 2: Exploratory Data Analysis & Visualizations"):
        chart_paths = generate_all_charts()
        logger.info(f"Generated {len(chart_paths)} charts in {paths['charts']}")

    with Timer("Step 3: Leakage-Free Model Evaluation & Benchmarking"):
        eval_df = run_full_evaluation(k=10, max_eval_users=100)
        logger.info(f"Evaluation complete:\n{eval_df.to_string(index=False)}")

    with Timer("Step 4: Sample Recommendation Generation for Benchmark Users"):
        ratings, movies, _ = load_processed_data()
        hybrid = HybridRecommender(cf_type="user", weight_cf=0.5, weight_content=0.3, weight_popularity=0.2)
        hybrid.fit(ratings, movies)

        sample_users = [1, 42, 196, 99999]  # Includes cold start user
        for uid in sample_users:
            if uid == 99999:
                recs = hybrid.recommend(uid, top_n=10, favorite_genres=["Sci-Fi", "Action"])
                fname = recs_dir / "recommendations_user_cold_start.csv"
            else:
                recs = hybrid.recommend(uid, top_n=10)
                fname = recs_dir / f"recommendations_user_{uid}.csv"

            cols_to_export = ["movie_id", "clean_title", "year", "genres", "recommendation_score", "explanation"]
            available_cols = [c for c in cols_to_export if c in recs.columns]
            recs[available_cols].to_csv(fname, index=False)
            logger.info(f"Exported sample recommendations to {fname}")

    with Timer("Step 5: Executive PDF Project Report Compilation"):
        try:
            pdf_path = generate_pdf_report()
            logger.info(f"PDF report successfully generated: {pdf_path}")
        except Exception as e:
            logger.error(f"Failed to generate PDF report: {e}")

    logger.info("=" * 70)
    logger.info("[OK] CINEMATCH AI PIPELINE COMPLETE! ALL ASSETS GENERATED.")
    logger.info("To launch the web dashboard, run:")
    logger.info("    streamlit run app.py")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
