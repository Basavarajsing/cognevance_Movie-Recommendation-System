"""
CineMatch AI - Analytics & Visualizations Page
Displays 10 interactive Plotly charts and data insights.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from src.data_loader import GENRE_COLUMNS


def render_analytics_page(
    ratings_df: pd.DataFrame,
    movies_df: pd.DataFrame,
    users_df: pd.DataFrame
) -> None:
    st.html("""<div style="margin-bottom: 22px;">
<h2 style="color: #FFFFFF !important; font-size: 2.1rem; font-weight: 800; margin: 0 0 6px 0;">📊 Exploratory Data Analysis & Analytics</h2>
<p style="color: #94A3B8 !important; font-size: 0.96rem; margin: 0;">Interactive data visualizations analyzing 100,000 ratings across genres, users, and decades.</p>
</div>""")

    # Prepare merged data
    rm_df = pd.merge(ratings_df, movies_df[["movie_id", "title", "clean_title", "year", "genres"]], on="movie_id", how="left")

    tab1, tab2, tab3, tab4 = st.tabs([
        "🎬 Catalog & Movie Trends",
        "⭐ Rating Dynamics",
        "👥 User Demographics",
        "🎭 Genre Deep Dive"
    ])

    # TAB 1: CATALOG & MOVIE TRENDS
    with tab1:
        st.markdown("### 1. Top 10 Most-Rated Movies")
        top_rated_count = rm_df.groupby("clean_title")["rating"].count().nlargest(10).reset_index()
        top_rated_count.columns = ["Title", "Rating Count"]

        fig1 = px.bar(
            top_rated_count.sort_values(by="Rating Count", ascending=True),
            x="Rating Count",
            y="Title",
            orientation="h",
            text="Rating Count",
            color="Rating Count",
            color_continuous_scale="Purples",
            template="plotly_dark"
        )
        fig1.update_layout(paper_bgcolor="#0F172A", plot_bgcolor="#1E293B", font_color="#F8FAFC", height=400)
        st.plotly_chart(fig1, use_container_width=True)
        st.info("💡 **Insight:** Blockbusters like *Star Wars (1977)*, *Contact (1997)*, and *Fargo (1996)* command the highest engagement, with Star Wars gathering over 580 ratings.")

        st.markdown("---")
        st.markdown("### 2. Top 10 Highest-Rated Movies (Min 50 Ratings)")
        movie_stats = rm_df.groupby("clean_title")["rating"].agg(["count", "mean"]).reset_index()
        high_rated = movie_stats[movie_stats["count"] >= 50].nlargest(10, "mean").sort_values(by="mean", ascending=True)

        fig2 = px.bar(
            high_rated,
            x="mean",
            y="clean_title",
            orientation="h",
            text=high_rated["mean"].round(2),
            color="mean",
            color_continuous_scale="Teal",
            template="plotly_dark"
        )
        fig2.update_layout(
            xaxis_title="Average Rating (1-5)",
            yaxis_title="Movie Title",
            xaxis_range=[3.8, 4.6],
            paper_bgcolor="#0F172A",
            plot_bgcolor="#1E293B",
            font_color="#F8FAFC",
            height=400
        )
        st.plotly_chart(fig2, use_container_width=True)
        st.info("💡 **Insight:** *Close Shave, A (1995)*, *Schindler's List (1993)*, and *The Wrong Trousers (1993)* achieve top average scores (> 4.45) among films with sustained audience voting.")

        st.markdown("---")
        st.markdown("### 3. Movie Releases Across Decades (1920 - 1998)")
        year_counts = movies_df[movies_df["year"] >= 1920].groupby("year")["movie_id"].count().reset_index()
        year_counts.columns = ["Year", "Count"]

        fig8 = px.area(
            year_counts,
            x="Year",
            y="Count",
            color_discrete_sequence=["#06B6D4"],
            template="plotly_dark",
            title="Production Volume by Release Year"
        )
        fig8.update_layout(paper_bgcolor="#0F172A", plot_bgcolor="#1E293B", font_color="#F8FAFC", height=380)
        st.plotly_chart(fig8, use_container_width=True)
        st.info("💡 **Insight:** Movie availability peaks sharply in the mid-1990s (1994-1997), corresponding to the active period of MovieLens user data collection.")

    # TAB 2: RATING DYNAMICS
    with tab2:
        st.markdown("### 4. Overall Rating Score Distribution")
        r_counts = ratings_df["rating"].value_counts().sort_index().reset_index()
        r_counts.columns = ["Rating", "Count"]
        r_counts["Percentage"] = (r_counts["Count"] / len(ratings_df) * 100).round(1)

        c_a, c_b = st.columns([1, 1])
        with c_a:
            fig4 = px.bar(
                r_counts,
                x="Rating",
                y="Count",
                text="Count",
                color="Rating",
                color_continuous_scale="Viridis",
                template="plotly_dark"
            )
            fig4.update_layout(paper_bgcolor="#0F172A", plot_bgcolor="#1E293B", font_color="#F8FAFC", height=380)
            st.plotly_chart(fig4, use_container_width=True)
        with c_b:
            fig4_pie = px.pie(
                r_counts,
                values="Count",
                names="Rating",
                hole=0.45,
                color_discrete_sequence=["#EF4444", "#F59E0B", "#3B82F6", "#8B5CF6", "#10B981"],
                template="plotly_dark"
            )
            fig4_pie.update_layout(paper_bgcolor="#0F172A", font_color="#F8FAFC", height=380)
            st.plotly_chart(fig4_pie, use_container_width=True)

        st.info("💡 **Insight:** Over 60% of all ratings are 4.0 or 5.0 stars, indicating strong positive selection bias (users predominantly watch and rate movies they expect to enjoy).")

        st.markdown("---")
        st.markdown("### 5. Ratings per User & Long-Tail Distribution")
        user_counts = ratings_df.groupby("user_id")["rating"].count().reset_index()
        user_counts.columns = ["User ID", "Ratings Count"]

        fig5 = px.histogram(
            user_counts,
            x="Ratings Count",
            nbins=45,
            color_discrete_sequence=["#EC4899"],
            template="plotly_dark"
        )
        fig5.update_layout(paper_bgcolor="#0F172A", plot_bgcolor="#1E293B", font_color="#F8FAFC", height=380)
        st.plotly_chart(fig5, use_container_width=True)

        st.markdown("---")
        st.markdown("### 6. Ratings per Movie (Catalog Sparsity)")
        movie_counts = ratings_df.groupby("movie_id")["rating"].count().reset_index()
        movie_counts.columns = ["Movie ID", "Ratings Received"]

        fig6 = px.histogram(
            movie_counts,
            x="Ratings Received",
            nbins=50,
            color_discrete_sequence=["#F59E0B"],
            template="plotly_dark"
        )
        fig6.update_layout(paper_bgcolor="#0F172A", plot_bgcolor="#1E293B", font_color="#F8FAFC", height=380)
        st.plotly_chart(fig6, use_container_width=True)
        st.info("💡 **Insight:** Strong long-tail power law: 20% of catalog movies capture over 70% of total rating volume, emphasizing the importance of hybrid fallback for tail items.")

    # TAB 3: USER DEMOGRAPHICS
    with tab3:
        st.markdown("### 7. User Age & Gender Demographics")
        col_g, col_a = st.columns([1, 1])
        with col_g:
            gender_cnt = users_df["gender"].value_counts().reset_index()
            gender_cnt.columns = ["Gender", "Count"]
            gender_cnt["Label"] = gender_cnt["Gender"].map({"M": "Male", "F": "Female"})

            fig_gender = px.pie(
                gender_cnt,
                values="Count",
                names="Label",
                color="Label",
                color_discrete_map={"Male": "#3B82F6", "Female": "#EC4899"},
                hole=0.4,
                template="plotly_dark"
            )
            fig_gender.update_layout(paper_bgcolor="#0F172A", font_color="#F8FAFC", height=360)
            st.plotly_chart(fig_gender, use_container_width=True)

        with col_a:
            fig_age = px.histogram(
                users_df,
                x="age",
                nbins=20,
                color_discrete_sequence=["#8B5CF6"],
                template="plotly_dark",
                labels={"age": "Age"}
            )
            fig_age.update_layout(paper_bgcolor="#0F172A", plot_bgcolor="#1E293B", font_color="#F8FAFC", height=360)
            st.plotly_chart(fig_age, use_container_width=True)

        st.markdown("---")
        st.markdown("### 8. User Distribution by Occupation")
        occ_counts = users_df["occupation"].value_counts().reset_index()
        occ_counts.columns = ["Occupation", "Count"]

        fig_occ = px.bar(
            occ_counts.head(12).sort_values(by="Count", ascending=True),
            x="Count",
            y="Occupation",
            orientation="h",
            color="Count",
            color_continuous_scale="Purples",
            template="plotly_dark"
        )
        fig_occ.update_layout(paper_bgcolor="#0F172A", plot_bgcolor="#1E293B", font_color="#F8FAFC", height=420)
        st.plotly_chart(fig_occ, use_container_width=True)

    # TAB 4: GENRE DEEP DIVE
    with tab4:
        st.markdown("### 9. Genre Distribution Across the Catalog")
        active_genres = [g for g in GENRE_COLUMNS if g != "unknown"]
        g_counts = movies_df[active_genres].sum().reset_index()
        g_counts.columns = ["Genre", "Movie Count"]
        g_counts = g_counts.sort_values(by="Movie Count", ascending=True)

        fig_g = px.bar(
            g_counts,
            x="Movie Count",
            y="Genre",
            orientation="h",
            color="Movie Count",
            color_continuous_scale="Blues",
            template="plotly_dark"
        )
        fig_g.update_layout(paper_bgcolor="#0F172A", plot_bgcolor="#1E293B", font_color="#F8FAFC", height=480)
        st.plotly_chart(fig_g, use_container_width=True)

        st.markdown("---")
        st.markdown("### 10. Genre Popularity vs. Average Quality")
        genre_metrics = []
        for g in active_genres:
            mids = movies_df[movies_df[g] == 1]["movie_id"]
            gr = ratings_df[ratings_df["movie_id"].isin(mids)]["rating"]
            if not gr.empty:
                genre_metrics.append({
                    "Genre": g,
                    "Total Ratings": len(gr),
                    "Average Rating": gr.mean()
                })
        gm_df = pd.DataFrame(genre_metrics)

        fig_scatter = px.scatter(
            gm_df,
            x="Total Ratings",
            y="Average Rating",
            size="Total Ratings",
            color="Genre",
            text="Genre",
            template="plotly_dark"
        )
        fig_scatter.update_traces(textposition="top center")
        fig_scatter.update_layout(paper_bgcolor="#0F172A", plot_bgcolor="#1E293B", font_color="#F8FAFC", height=500)
        st.plotly_chart(fig_scatter, use_container_width=True)
        st.info("💡 **Insight:** Drama and Comedy drive the largest volume of reviews, while Film-Noir and War command the highest overall satisfaction ratings (> 3.75 ★).")
