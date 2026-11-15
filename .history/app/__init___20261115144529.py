"""
CineMatch AI - Streamlit Web Application Package
"""

import streamlit as st


def _safe_html(markup: str, **kwargs) -> None:
    """Render HTML markup without exposing the source code in the app UI."""
    st.markdown(markup, unsafe_allow_html=True, **kwargs)


# streamlit does not reliably expose a working .html renderer in all versions.
# Patch the actual module object so every page renders HTML, not raw source.
if not hasattr(st, "html"):
    st.html = _safe_html

if not hasattr(st.sidebar, "html"):
    st.sidebar.html = _safe_html
