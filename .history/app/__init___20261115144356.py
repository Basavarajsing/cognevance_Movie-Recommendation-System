"""
CineMatch AI - Streamlit Web Application Package
"""

import streamlit as st


def _safe_html(markup: str, **kwargs) -> None:
    """Render HTML markup without exposing the source code in the app UI."""
    st.markdown(markup, unsafe_allow_html=True, **kwargs)


# Streamlit may expose a broken/stubbed html helper in some environments.
# Normalize it so every page keeps rendering actual HTML instead of literal tags.
st.html = _safe_html
