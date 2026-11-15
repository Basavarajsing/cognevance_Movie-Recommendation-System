"""
CineMatch AI - About Project & Developer Information Page
"""

import streamlit as st


def render_about_page() -> None:
    st.html("""<div style="margin-bottom: 22px;">
<h2 style="color: #FFFFFF !important; font-size: 2.1rem; font-weight: 800; margin: 0 0 6px 0;">ℹ️ About CineMatch AI</h2>
<p style="color: #94A3B8 !important; font-size: 0.96rem; margin: 0;">Architecture, Technology Stack, Machine Learning Methodology & Developer Profile.</p>
</div>""")

    # Project Overview Cards
    col_ov, col_arch = st.columns([1, 1])
    with col_ov:
        st.markdown("""
        ### 🎯 Project Objectives
        - **Intelligent Personalization:** Deliver high-precision recommendations by leveraging both behavioral community signals and item characteristics.
        - **Explainability:** Provide human-readable, model-grounded explanations for every recommended title.
        - **Cold-Start Resilience:** Seamlessly transition new users from popularity/genre fallbacks to personalized collaborative filtering as their rating history matures.
        - **Production-Grade Architecture:** Modular design, strict leakage-free evaluation, SQLite local state persistence, and responsive cinematic UI.
        """)

    with col_arch:
        st.markdown("""
        ### 🛠️ Technology Stack
        - **Core Language:** Python 3.13
        - **Data Processing:** Pandas, NumPy, SciPy
        - **Machine Learning:** Scikit-learn (Cosine Similarity, TF-IDF, Vector Normalization)
        - **Visualization:** Plotly Interactive Dashboards, Matplotlib, Seaborn
        - **Application Framework:** Streamlit (Custom Dark Cinematic Theme)
        - **Database:** SQLite (cinematch.db)
        - **Serialization & Caching:** Joblib, Streamlit State Caching
        - **Testing & Verification:** Pytest Test Suite
        - **Report Generation:** ReportLab PDF Engine
        """)

    st.markdown("---")

    # Architecture Overview
    st.markdown("### 🏛️ System Architecture")
    st.markdown("""
    ```
    ┌────────────────────────────────────────────────────────────────────────┐
    │                         CineMatch AI Platform                          │
    └────────────────────────────────────────────────────────────────────────┘
                                    │
            ┌───────────────────────┴───────────────────────┐
            ▼                                               ▼
    ┌───────────────────────────┐               ┌───────────────────────────┐
    │     Data Pipeline         │               │     Local Database        │
    │  - MovieLens 100K         │               │  - SQLite (cinematch.db)  │
    │  - Preprocessing & Clean  │               │  - Custom Ratings         │
    │  - Validation & Splits    │               │  - User Preferences       │
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
    """)

    st.markdown("---")

    # Developer Information Section
    st.markdown("### 👨‍💻 Developer Information")
    st.markdown("""
    <div style="background: linear-gradient(145deg, #1E293B, #0F172A); border: 1px solid rgba(139, 92, 246, 0.3); border-radius: 16px; padding: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.3);">
        <div style="display: flex; align-items: center; gap: 20px; flex-wrap: wrap;">
            <div style="width: 80px; height: 80px; border-radius: 50%; background: linear-gradient(135deg, #6366F1, #EC4899); display: flex; align-items: center; justify-content: center; font-size: 32px; color: #FFF; font-weight: 800; box-shadow: 0 4px 15px rgba(99,102,241,0.4);">
                CM
            </div>
            <div>
                <h3 style="margin: 0; color: #FFFFFF; font-size: 1.5rem;">CineMatch AI Developer</h3>
                <p style="margin: 4px 0 0 0; color: #A78BFA; font-weight: 600;">Senior Python Developer & Machine Learning Engineer</p>
                <p style="margin: 4px 0 0 0; color: #94A3B8; font-size: 0.9rem;">Specialization: Machine Learning, Recommender Systems, Data Science & Full-Stack AI Dashboards</p>
            </div>
        </div>
        <hr style="border-color: rgba(255,255,255,0.08); margin: 20px 0;">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px;">
            <div>
                <span style="color: #64748B; font-size: 0.8rem; text-transform: uppercase; font-weight: 700;">Portfolio / Project</span><br/>
                <span style="color: #F1F5F9; font-weight: 600;">CineMatch AI Platform</span>
            </div>
            <div>
                <span style="color: #64748B; font-size: 0.8rem; text-transform: uppercase; font-weight: 700;">Email Contact</span><br/>
                <span style="color: #F1F5F9; font-weight: 600;">developer@cinematch.ai</span>
            </div>
            <div>
                <span style="color: #64748B; font-size: 0.8rem; text-transform: uppercase; font-weight: 700;">GitHub Repository</span><br/>
                <span style="color: #F1F5F9; font-weight: 600;">github.com/developer/cinematch-ai</span>
            </div>
            <div>
                <span style="color: #64748B; font-size: 0.8rem; text-transform: uppercase; font-weight: 700;">License</span><br/>
                <span style="color: #F1F5F9; font-weight: 600;">MIT Open Source</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
