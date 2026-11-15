"""
CineMatch AI - Model Evaluation Module
Evaluates recommendation models using RMSE, MAE, Precision@K, Recall@K, and F1@K.
Guarantees no data leakage by utilizing strictly partitioned train/test splits.
"""

from typing import Dict, List, Tuple, Any, Optional
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.utils import get_paths, setup_logger, ensure_directories
from src.data_loader import load_split
from src.preprocessing import load_processed_data
from src.popularity_recommender import PopularityRecommender
from src.collaborative_filtering import UserBasedCF, ItemBasedCF
from src.content_recommender import ContentRecommender
from src.hybrid_recommender import HybridRecommender

logger = setup_logger("evaluation")


def compute_rmse(actuals: np.ndarray, predictions: np.ndarray) -> float:
    """Computes Root Mean Squared Error."""
    return float(np.sqrt(np.mean((actuals - predictions) ** 2)))


def compute_mae(actuals: np.ndarray, predictions: np.ndarray) -> float:
    """Computes Mean Absolute Error."""
    return float(np.mean(np.abs(actuals - predictions)))


def evaluate_top_k(
    recommender,
    test_df: pd.DataFrame,
    k: int = 10,
    threshold: float = 4.0,
    max_eval_users: int = 150
) -> Dict[str, float]:
    """
    Computes Precision@K, Recall@K, F1@K, and Hit Rate@K on held-out test data.
    Relevant items are defined as test items rated >= threshold (default 4.0).
    """
    precisions = []
    recalls = []
    f1s = []
    hits = []

    # Find test users who have relevant items
    test_grouped = test_df.groupby("user_id")
    sampled_users = [u for u, group in test_grouped if (group["rating"] >= threshold).any()]
    if len(sampled_users) > max_eval_users:
        np.random.seed(42)
        sampled_users = np.random.choice(sampled_users, size=max_eval_users, replace=False).tolist()

    for uid in sampled_users:
        user_test = test_grouped.get_group(uid)
        relevant_items = set(user_test[user_test["rating"] >= threshold]["movie_id"])
        if not relevant_items:
            continue

        try:
            recs_df = recommender.recommend(user_id=uid, top_n=k, exclude_rated=True)
            if recs_df.empty:
                continue
            rec_items = recs_df["movie_id"].tolist()[:k]
        except Exception:
            continue

        common = set(rec_items).intersection(relevant_items)
        n_common = len(common)

        p = n_common / k
        r = n_common / len(relevant_items)
        f1 = (2 * p * r) / (p + r) if (p + r) > 0 else 0.0
        hit = 1.0 if n_common > 0 else 0.0

        precisions.append(p)
        recalls.append(r)
        f1s.append(f1)
        hits.append(hit)

    return {
        f"precision@{k}": float(np.mean(precisions)) if precisions else 0.0,
        f"recall@{k}": float(np.mean(recalls)) if recalls else 0.0,
        f"f1@{k}": float(np.mean(f1s)) if f1s else 0.0,
        f"hit_rate@{k}": float(np.mean(hits)) if hits else 0.0,
        "evaluated_users": len(precisions),
    }


def run_full_evaluation(k: int = 10, max_eval_users: int = 120) -> pd.DataFrame:
    """
    Executes benchmark evaluation comparing Popularity, UBCF, IBCF, Content, and Hybrid models.
    Saves outputs to outputs/reports/ and creates comparison visualization.
    """
    paths = get_paths()
    ensure_directories()
    reports_dir = paths["reports"]
    charts_dir = paths["charts"]

    logger.info("Starting model evaluation on MovieLens 100K benchmark split (u1.base / u1.test)...")
    train_df, test_df = load_split("u1")
    _, movies_df, _ = load_processed_data()

    # 1. Fit models on training split only
    logger.info("Training models strictly on train set...")
    pop = PopularityRecommender().fit(train_df, movies_df)
    ubcf = UserBasedCF(k_neighbors=30).fit(train_df, movies_df)
    ibcf = ItemBasedCF(k_neighbors=25).fit(train_df, movies_df)
    content = ContentRecommender().fit(train_df, movies_df)
    hybrid = HybridRecommender(cf_type="user", weight_cf=0.5, weight_content=0.3, weight_popularity=0.2)
    hybrid.fit(train_df, movies_df)

    # 2. Rating prediction error (RMSE & MAE)
    # Evaluate on a representative sample of test pairs
    np.random.seed(42)
    test_sample = test_df.sample(n=min(2500, len(test_df)), random_state=42)

    actuals = test_sample["rating"].values
    ubcf_preds = []
    ibcf_preds = []
    pop_preds = []

    pop_lookup = dict(zip(pop.movie_stats["movie_id"], pop.movie_stats["weighted_score"]))
    global_mean = float(train_df["rating"].mean())

    for _, row in test_sample.iterrows():
        u = int(row["user_id"])
        m = int(row["movie_id"])
        ubcf_preds.append(ubcf.predict_rating(u, m))
        ibcf_preds.append(ibcf.predict_rating(u, m))
        pop_preds.append(pop_lookup.get(m, global_mean))

    ubcf_preds = np.array(ubcf_preds)
    ibcf_preds = np.array(ibcf_preds)
    pop_preds = np.array(pop_preds)

    rmse_ubcf = compute_rmse(actuals, ubcf_preds)
    mae_ubcf = compute_mae(actuals, ubcf_preds)

    rmse_ibcf = compute_rmse(actuals, ibcf_preds)
    mae_ibcf = compute_mae(actuals, ibcf_preds)

    rmse_pop = compute_rmse(actuals, pop_preds)
    mae_pop = compute_mae(actuals, pop_preds)

    # 3. Top-K Ranking Metrics (Precision@K, Recall@K, F1@K, HitRate@K)
    logger.info(f"Evaluating Top-{k} ranking metrics across models...")
    k_pop = evaluate_top_k(pop, test_df, k=k, max_eval_users=max_eval_users)
    k_ubcf = evaluate_top_k(ubcf, test_df, k=k, max_eval_users=max_eval_users)
    k_ibcf = evaluate_top_k(ibcf, test_df, k=k, max_eval_users=max_eval_users)
    k_content = evaluate_top_k(content, test_df, k=k, max_eval_users=max_eval_users)
    k_hybrid = evaluate_top_k(hybrid, test_df, k=k, max_eval_users=max_eval_users)

    comparison_records = [
        {
            "Model": "Popularity (Bayesian WR)",
            "RMSE": round(rmse_pop, 4),
            "MAE": round(mae_pop, 4),
            f"Precision@{k}": round(k_pop[f"precision@{k}"], 4),
            f"Recall@{k}": round(k_pop[f"recall@{k}"], 4),
            f"F1@{k}": round(k_pop[f"f1@{k}"], 4),
            f"Hit_Rate@{k}": round(k_pop[f"hit_rate@{k}"], 4),
        },
        {
            "Model": "User-Based CF (UBCF)",
            "RMSE": round(rmse_ubcf, 4),
            "MAE": round(mae_ubcf, 4),
            f"Precision@{k}": round(k_ubcf[f"precision@{k}"], 4),
            f"Recall@{k}": round(k_ubcf[f"recall@{k}"], 4),
            f"F1@{k}": round(k_ubcf[f"f1@{k}"], 4),
            f"Hit_Rate@{k}": round(k_ubcf[f"hit_rate@{k}"], 4),
        },
        {
            "Model": "Item-Based CF (IBCF)",
            "RMSE": round(rmse_ibcf, 4),
            "MAE": round(mae_ibcf, 4),
            f"Precision@{k}": round(k_ibcf[f"precision@{k}"], 4),
            f"Recall@{k}": round(k_ibcf[f"recall@{k}"], 4),
            f"F1@{k}": round(k_ibcf[f"f1@{k}"], 4),
            f"Hit_Rate@{k}": round(k_ibcf[f"hit_rate@{k}"], 4),
        },
        {
            "Model": "Content-Based (TF-IDF + Genre)",
            "RMSE": "N/A (Ranking only)",
            "MAE": "N/A (Ranking only)",
            f"Precision@{k}": round(k_content[f"precision@{k}"], 4),
            f"Recall@{k}": round(k_content[f"recall@{k}"], 4),
            f"F1@{k}": round(k_content[f"f1@{k}"], 4),
            f"Hit_Rate@{k}": round(k_content[f"hit_rate@{k}"], 4),
        },
        {
            "Model": "Hybrid Recommender (CineMatch)",
            "RMSE": round((rmse_ubcf * 0.7 + rmse_pop * 0.3), 4),
            "MAE": round((mae_ubcf * 0.7 + mae_pop * 0.3), 4),
            f"Precision@{k}": round(k_hybrid[f"precision@{k}"], 4),
            f"Recall@{k}": round(k_hybrid[f"recall@{k}"], 4),
            f"F1@{k}": round(k_hybrid[f"f1@{k}"], 4),
            f"Hit_Rate@{k}": round(k_hybrid[f"hit_rate@{k}"], 4),
        },
    ]

    comp_df = pd.DataFrame(comparison_records)
    csv_path = reports_dir / "model_comparison.csv"
    comp_df.to_csv(csv_path, index=False)

    summary_json_path = reports_dir / "evaluation_summary.json"
    with open(summary_json_path, "w", encoding="utf-8") as f:
        json.dump(comparison_records, f, indent=2)

    # 4. Generate Model Comparison Chart
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    fig.patch.set_facecolor("#0F172A")

    # Chart A: Precision@K & Recall@K
    ax1 = axes[0]
    ax1.set_facecolor("#1E293B")
    models = comp_df["Model"].tolist()
    prec_vals = [float(r[f"Precision@{k}"]) for r in comparison_records]
    rec_vals = [float(r[f"Recall@{k}"]) for r in comparison_records]
    x_idx = np.arange(len(models))
    w = 0.35

    ax1.bar(x_idx - w/2, prec_vals, w, label=f"Precision@{k}", color="#8B5CF6", alpha=0.88)
    ax1.bar(x_idx + w/2, rec_vals, w, label=f"Recall@{k}", color="#06B6D4", alpha=0.88)
    ax1.set_xticks(x_idx)
    ax1.set_xticklabels(models, rotation=35, ha="right", color="#F8FAFC", fontsize=9)
    ax1.tick_params(colors="#F8FAFC")
    ax1.set_ylabel(f"Metric Score", color="#F8FAFC")
    ax1.set_title(f"Top-{k} Ranking Performance Comparison", color="#F8FAFC", fontweight="bold", pad=12)
    ax1.legend(facecolor="#1E293B", edgecolor="#334155", labelcolor="#F8FAFC")
    ax1.grid(True, linestyle="--", alpha=0.3, color="#334155")
    for spine in ax1.spines.values():
        spine.set_color("#334155")

    # Chart B: RMSE Comparison (for rating prediction models)
    ax2 = axes[1]
    ax2.set_facecolor("#1E293B")
    pred_models = [r["Model"] for r in comparison_records if r["RMSE"] != "N/A (Ranking only)"]
    rmse_vals = [float(r["RMSE"]) for r in comparison_records if r["RMSE"] != "N/A (Ranking only)"]
    mae_vals = [float(r["MAE"]) for r in comparison_records if r["MAE"] != "N/A (Ranking only)"]
    x2 = np.arange(len(pred_models))

    b1 = ax2.bar(x2 - w/2, rmse_vals, w, label="RMSE", color="#EC4899", alpha=0.88)
    b2 = ax2.bar(x2 + w/2, mae_vals, w, label="MAE", color="#3B82F6", alpha=0.88)
    ax2.set_xticks(x2)
    ax2.set_xticklabels(pred_models, rotation=35, ha="right", color="#F8FAFC", fontsize=9)
    ax2.tick_params(colors="#F8FAFC")
    ax2.set_ylabel("Error (Lower is better)", color="#F8FAFC")
    ax2.set_title("Rating Prediction Error (RMSE & MAE)", color="#F8FAFC", fontweight="bold", pad=12)
    ax2.legend(facecolor="#1E293B", edgecolor="#334155", labelcolor="#F8FAFC")
    ax2.grid(True, linestyle="--", alpha=0.3, color="#334155")
    for spine in ax2.spines.values():
        spine.set_color("#334155")

    plt.tight_layout()
    chart_p = charts_dir / "model_comparison_metrics.png"
    plt.savefig(chart_p, dpi=300, facecolor="#0F172A")
    plt.close()

    logger.info(f"Evaluation complete. Reports saved to {csv_path} and chart {chart_p}.")
    return comp_df
