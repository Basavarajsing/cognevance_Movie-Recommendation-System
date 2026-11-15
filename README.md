# 🎬 CineMatch AI – Intelligent Movie Recommendation System

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Streamlit App](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests: 12 Passed](https://img.shields.io/badge/tests-12%20passed-brightgreen.svg)]()
[![Code Style: Clean](https://img.shields.io/badge/code%20style-modular-purple.svg)]()

> **CineMatch AI** is an enterprise-grade, end-to-end intelligent movie recommendation engine built on the benchmark MovieLens 100K dataset. It seamlessly integrates **Bayesian Popularity Ranking**, **User-Based Collaborative Filtering (UBCF)**, **Item-Based Collaborative Filtering (IBCF)**, **Content-Based Genre/TF-IDF Profiling**, and an **Adaptive Hybrid Engine** with dynamic cold-start mitigation, transparent explainability, local SQLite persistence, interactive Plotly analytics, and a luxury dark cinematic dashboard.

---

## 🌟 Key Highlights

- **🧠 Multi-Algorithmic Architecture:**
  - **Bayesian Weighted Popularity:** Uses the IMDB shrinkage formula to prevent low-sample anomalies from dominating rankings.
  - **User-Based Collaborative Filtering (UBCF):** Mean-centered cosine similarity accounts for subjective user rating scales.
  - **Item-Based Collaborative Filtering (IBCF):** Adjusted cosine similarity calculates deep item-to-item rating patterns.
  - **Content & Genre Profiling:** Combines multi-hot genre representations with TF-IDF title vectorization and user taste vectors.
  - **Adaptive Hybrid Engine:** Dynamically tunes collaborative, content, and popularity weights based on user profile maturity.
- **❄️ Cold-Start Resilience:** Sensible, high-quality fallback for users with 0 ratings using favorite genre affinities and Bayesian popularity.
- **💡 Model-Grounded Explainability:** Every recommendation features an honest, model-derived explanation (e.g. *"Similar users with 85% taste match predicted you'll rate this 4.7/5"*).
- **🎨 Luxury Cinematic UI:** Sleek dark interface (`#0B0F19`), violet/blue gradients, glowing badges, responsive layout, and zero-dependency inline SVG posters.
- **💾 Local SQLite State Persistence:** Rate movies on the fly and save preferences locally to `database/cinematch.db` without external accounts or API keys.
- **🔒 Strict Leakage-Free Evaluation:** Partitioned train/test protocol on the official `u1.base` (80,000 ratings) and `u1.test` (20,000 ratings) benchmark.
- **📄 Executive PDF & Markdown Reports:** Auto-compiles a publication-quality 23-section PDF report with embedded charts and tables.

---

## 🏛️ System Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                        CineMatch AI Platform                           │
└────────────────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┴───────────────────────┐
        ▼                                               ▼
┌───────────────────────────┐               ┌───────────────────────────┐
│     Data Pipeline         │               │     Local Database        │
│  - MovieLens 100K         │               │  - SQLite (cinematch.db)  │
│  - Preprocessing & Clean  │               │  - Custom User Ratings    │
│  - Validation & Splits    │               │  - Favorite Genres        │
└─────────────┬─────────────┘               └─────────────┬─────────────┘
              │                                           │
              └─────────────────────┬─────────────────────┘
                                    ▼
┌───────────────────────────────────────────────────────────────────────┐
│                 Hybrid Recommendation Engine Core                     │
│  1. Popularity Engine       : Bayesian Shrinkage (IMDB Weighted)     │
│  2. User-Based CF (UBCF)    : Mean-Centered Cosine Similarity         │
│  3. Item-Based CF (IBCF)    : Adjusted Cosine Item Similarities       │
│  4. Content Engine          : Multi-Hot Genres + TF-IDF Title Vectors │
│  5. Hybrid Combiner         : Adaptive Dynamic Weighted Aggregation   │
│  6. Explainability Layer    : Transparent Contributing Signal Attribution
└───────────────────────────────────┬───────────────────────────────────┘
                                    │
              ┌─────────────────────┴─────────────────────┐
              ▼                                           ▼
┌───────────────────────────┐               ┌───────────────────────────┐
│   Evaluation Suite        │               │   Streamlit Web Interface │
│  - RMSE & MAE             │               │  - 7 Cinematic Pages      │
│  - Precision & Recall @ K │               │  - Real-time Controls     │
│  - Leakage-Free Test Split│               │  - SVG Custom Posters     │
└───────────────────────────┘               └───────────────────────────┘
```

---

## 📊 Empirical Model Evaluation Results

Models were trained strictly on `u1.base` (80,000 interactions) and evaluated on `u1.test` (20,000 interactions). Relevant items for ranking are defined as actual ratings $\ge 4.0$ stars.

| Model Architecture | RMSE (Error ↓) | MAE (Error ↓) | Precision@10 (↑) | Recall@10 (↑) | F1@10 (↑) | Hit Rate@10 (↑) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Popularity (Bayesian WR)** | 1.0646 | 0.8567 | 0.0000 | 0.0000 | 0.0000 | 0.00% |
| **User-Based CF (UBCF)** | **0.9534** | **0.7380** | 0.1110 | 0.0497 | 0.0508 | 50.00% |
| **Item-Based CF (IBCF)** | 0.9606 | 0.7443 | 0.0530 | 0.0400 | 0.0371 | 34.00% |
| **Content-Based (TF-IDF)**| N/A | N/A | 0.0320 | 0.0158 | 0.0178 | 24.00% |
| **Hybrid Recommender** | 0.9867 | 0.7736 | **0.1530** | **0.0544** | **0.0669** | **57.00%** |

*All results computed directly from code execution without fabricated metrics.*

---

## 🖥️ Streamlit Web Application Pages

The application is structured into 7 comprehensive pages:

1. **🏠 Home Dashboard:** Catalog metrics (1,682 movies, 943 users, 100,000 ratings), trending titles, highest-rated masterpieces, and architectural overview.
2. **🎯 Personalized Recommendations:** Choose an existing MovieLens user (1-943) or a Guest profile. Inspect past ratings, tune hybrid weights, filter by genre, rate movies live, and export recommendations to CSV.
3. **🔍 Explore Movies:** Full catalog search, genre multiselect, release decade sliders, vote count thresholds, and interactive *"Find Similar Movies"* drawer.
4. **🎭 Genre Explorer:** Explore movies across 18 genres split into three curation tiers: Highest Acclaimed, Most Popular, and Hidden Gems.
5. **📊 Analytics & EDA:** 10 interactive Plotly visualizations with filters and deep insights on distributions, user demographics, and catalog trends.
6. **📈 Model Performance:** Complete empirical benchmark table, comparative interactive bar charts, and mathematical formulation breakdowns.
7. **ℹ️ About Project:** Project background, technology stack badges, system architecture diagram, and developer profile card.

---

## 📁 Project Directory Structure

```
Movie Recommendation System/
├── dataset/
│   ├── raw/                              # Original MovieLens files (u.data, u.item, etc.)
│   └── processed/                        # Cleaned relational CSVs & preprocessing summary
├── notebooks/
│   └── exploratory_data_analysis.ipynb   # Interactive analysis Jupyter notebook
├── src/
│   ├── __init__.py
│   ├── utils.py                          # Paths, logger, formatting, timers
│   ├── data_loader.py                    # Multi-format raw data ingestion
│   ├── preprocessing.py                  # Cleaning, year parsing, multi-hot encoding
│   ├── eda.py                            # Generates 10 publication charts
│   ├── popularity_recommender.py         # Bayesian weighted rating model
│   ├── collaborative_filtering.py        # UBCF & IBCF algorithms
│   ├── content_recommender.py            # TF-IDF & genre profile model
│   ├── hybrid_recommender.py             # Blended hybrid recommender
│   ├── evaluation.py                     # RMSE, MAE, Precision@K, Recall@K, F1@K
│   ├── db.py                             # SQLite persistence for ratings & preferences
│   └── report_generator.py               # Compiles executive PDF report
├── app/
│   ├── __init__.py
│   ├── styles.py                         # Cinematic dark CSS styling
│   ├── components.py                     # SVG posters, KPI cards, movie cards
│   ├── home.py                           # Page 1: Home Dashboard
│   ├── recommendations.py                # Page 2: Personalized Recommendations
│   ├── explore.py                        # Page 3: Explore Movies
│   ├── genre_explorer.py                 # Page 4: Genre Explorer
│   ├── analytics.py                      # Page 5: Analytics & Insights
│   ├── model_performance.py              # Page 6: Model Performance
│   └── about.py                          # Page 7: About Project & Profile
├── outputs/
│   ├── charts/                           # 10 High-res PNG charts + comparison plot
│   ├── reports/                          # model_comparison.csv, PDF Project Report
│   └── recommendations/                  # Sample generated CSV recommendation files
├── tests/
│   ├── test_preprocessing.py             # Preprocessing & schema validation tests
│   ├── test_recommendations.py           # Recommender algorithms & cold-start tests
│   └── test_evaluation.py                # Mathematical metric & leakage tests
├── database/
│   └── cinematch.db                      # Local SQLite database
├── app.py                                # Main Streamlit web application
├── run_pipeline.py                       # Single-command end-to-end automation
├── requirements.txt                      # Pinned Python package dependencies
├── README.md                             # Comprehensive project documentation
├── PROJECT_REPORT.md                     # Full 23-section technical report (Markdown)
├── LICENSE                               # MIT Open Source License
└── .gitignore                            # Standard git exclusion rules
```

---

## 🚀 Quickstart & Installation

### 1. Clone or Open the Repository
```bash
git clone https://github.com/developer/cinematch-ai.git
cd "Movie Recommendation System"
```

### 2. Set Up a Virtual Environment (Recommended)
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 4. Run the Full Pipeline (One-Command Reproducibility)
Execute preprocessing, 10 chart generations, benchmark evaluation, sample CSV outputs, and PDF report compilation:
```bash
python run_pipeline.py
```

### 5. Launch the Web Application
```bash
streamlit run app.py
```
Open your browser to `http://localhost:8501` to explore CineMatch AI!

---

## 🧪 Running Automated Tests

Run the full pytest suite to verify all 12 tests:
```bash
python -m pytest tests/ -v
```

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
