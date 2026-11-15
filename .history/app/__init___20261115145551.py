"""
CineMatch AI - Streamlit Web Application Package
"""

import streamlit as st


def _safe_html(markup: str, **kwargs) -> None:
    """Render HTML markup without exposing the source code in the app UI."""
    st.markdown(markup, unsafe_allow_html=True, **kwargs)


# Streamlit does not reliably expose a working .html renderer across versions.
# Override it so every page renders HTML instead of literal source code.
st.html = _safe_html
st.sidebar.html = _safe_html
