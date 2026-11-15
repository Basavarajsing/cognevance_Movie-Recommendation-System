"""
CineMatch AI - Styling & Custom CSS Module
Provides a luxury cinematic dark theme with 100% visible high-contrast typography,
vibrant neon accents, and modern glassmorphism components.
"""

CUSTOM_CSS = """
<style>
/* Import Modern Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

/* Force Global Dark Theme & Crisp Typography */
html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: #0B0F19 !important;
    color: #F8FAFC !important;
}

/* Background Atmosphere Glow */
.stApp {
    background: radial-gradient(circle at 10% 10%, rgba(99, 102, 241, 0.12) 0%, transparent 45%),
                radial-gradient(circle at 90% 90%, rgba(139, 92, 246, 0.12) 0%, transparent 45%),
                #0B0F19 !important;
}

/* Universal Typography & Heading Colors (Ensures 100% text visibility) */
h1, h2, h3, h4, h5, h6 {
    color: #FFFFFF !important;
    font-weight: 700 !important;
    letter-spacing: -0.3px !important;
}
p, span, div, li, label {
    color: #E2E8F0 !important;
}
.stCaption, small {
    color: #94A3B8 !important;
    font-size: 0.85rem !important;
}

/* Page Title with Glowing Gradient */
.page-title {
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #FFFFFF 30%, #C4B5FD 70%, #38BDF8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 6px;
    letter-spacing: -0.5px;
}
.page-subtitle {
    color: #94A3B8 !important;
    font-size: 1rem;
    margin-bottom: 24px;
    line-height: 1.5;
}

/* Sidebar Customization */
section[data-testid="stSidebar"] {
    background-color: #0C111E !important;
    border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
}
section[data-testid="stSidebar"] * {
    color: #E2E8F0 !important;
}
section[data-testid="stSidebar"] .stRadio label span {
    color: #F1F5F9 !important;
    font-weight: 500 !important;
}

/* High Contrast Input Labels & Widgets */
div[data-testid="stRadio"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stSlider"] label,
div[data-testid="stTextInput"] label,
div[data-testid="stMultiselect"] label {
    color: #F8FAFC !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    margin-bottom: 4px !important;
}

/* Radio button options text */
div[data-testid="stRadio"] div[role="radiogroup"] label span {
    color: #F1F5F9 !important;
    font-size: 0.92rem !important;
    font-weight: 500 !important;
}

/* Custom Selectbox & Inputs */
div[data-baseweb="select"] {
    background-color: #161F30 !important;
    border: 1px solid rgba(139, 92, 246, 0.3) !important;
    border-radius: 10px !important;
    color: #FFFFFF !important;
}
div[data-baseweb="select"] * {
    color: #FFFFFF !important;
}
input[type="text"] {
    background-color: #161F30 !important;
    border: 1px solid rgba(139, 92, 246, 0.3) !important;
    color: #FFFFFF !important;
    border-radius: 10px !important;
}

/* Expander Dark Card Styling (Replaces light/white box) */
div[data-testid="stExpander"] {
    background-color: #121829 !important;
    border: 1px solid rgba(139, 92, 246, 0.35) !important;
    border-radius: 14px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35) !important;
    margin-bottom: 20px !important;
    overflow: hidden !important;
}
div[data-testid="stExpander"] summary {
    background-color: #161F30 !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 12px 18px !important;
}
div[data-testid="stExpander"] summary:hover {
    color: #A78BFA !important;
}
div[data-testid="stExpander"] div[role="region"] {
    background-color: #121829 !important;
    padding: 16px 20px !important;
}

/* Tabs Styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px !important;
    background-color: transparent !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
}
.stTabs [data-baseweb="tab"] {
    background-color: #161F30 !important;
    border-radius: 8px 8px 0 0 !important;
    color: #94A3B8 !important;
    font-weight: 600 !important;
    padding: 10px 22px !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-bottom: none !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(180deg, #1E293B, #161F30) !important;
    color: #A78BFA !important;
    border-top: 2px solid #8B5CF6 !important;
    font-weight: 700 !important;
}

/* Alert Boxes & Callouts */
div[data-testid="stAlert"] {
    background-color: rgba(99, 102, 241, 0.12) !important;
    border: 1px solid rgba(99, 102, 241, 0.4) !important;
    border-radius: 12px !important;
    color: #E2E8F0 !important;
}
div[data-testid="stAlert"] * {
    color: #F1F5F9 !important;
}

/* Metric KPI Card */
.cinematch-metric-card {
    background: linear-gradient(145deg, #161F30, #0F172A);
    border: 1px solid rgba(139, 92, 246, 0.3);
    border-radius: 16px;
    padding: 22px 16px;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    transition: transform 0.25s ease, border-color 0.25s ease;
}
.cinematch-metric-card:hover {
    transform: translateY(-4px);
    border-color: #8B5CF6;
    box-shadow: 0 8px 25px rgba(139, 92, 246, 0.25);
}
.cinematch-metric-val {
    font-size: 2.3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #FFFFFF, #C4B5FD);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 4px 0;
}
.cinematch-metric-title {
    font-size: 0.85rem;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    font-weight: 700;
}
.cinematch-metric-sub {
    font-size: 0.75rem;
    color: #64748B;
    margin-top: 2px;
}

/* Cinematic Movie Card */
.movie-card-container {
    background: linear-gradient(180deg, #151D2E 0%, #0F1626 100%);
    border: 1px solid rgba(139, 92, 246, 0.25);
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 22px;
    box-shadow: 0 6px 22px rgba(0, 0, 0, 0.5);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.movie-card-container:hover {
    transform: translateY(-6px);
    border-color: #8B5CF6;
    box-shadow: 0 12px 32px rgba(139, 92, 246, 0.3);
}
.movie-card-body {
    padding: 16px;
}
.movie-title-text {
    font-size: 1.12rem;
    font-weight: 800;
    color: #FFFFFF !important;
    margin: 0 0 6px 0;
    line-height: 1.35;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.movie-year-tag {
    display: inline-block;
    background: rgba(139, 92, 246, 0.25);
    border: 1px solid rgba(139, 92, 246, 0.4);
    color: #C4B5FD !important;
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 700;
}
.score-badge-pill {
    background: linear-gradient(135deg, #7C3AED, #2563EB);
    color: #FFFFFF !important;
    padding: 4px 10px;
    border-radius: 10px;
    font-weight: 800;
    font-size: 0.88rem;
    box-shadow: 0 2px 10px rgba(124, 58, 237, 0.4);
    display: inline-flex;
    align-items: center;
    gap: 4px;
}
.genre-pills-row {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin: 10px 0;
}
.genre-badge-item {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.15);
    color: #E2E8F0 !important;
    font-size: 0.72rem;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 12px;
}
.explanation-callout {
    background: rgba(99, 102, 241, 0.12);
    border-left: 3px solid #8B5CF6;
    border-radius: 0 8px 8px 0;
    padding: 8px 12px;
    font-size: 0.82rem;
    color: #DDD6FE !important;
    line-height: 1.45;
    margin-top: 10px;
}
.explanation-callout * {
    color: #DDD6FE !important;
}

/* Action Button Row */
.card-actions-row {
    display: flex;
    gap: 8px;
    margin-top: 12px;
    padding-top: 10px;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
}
.card-action-btn {
    flex: 1;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.12);
    color: #CBD5E1 !important;
    text-align: center;
    padding: 5px 8px;
    border-radius: 8px;
    font-size: 0.75rem;
    font-weight: 600;
    text-decoration: none;
    transition: all 0.2s ease;
    display: inline-block;
}
.card-action-btn:hover {
    background: rgba(139, 92, 246, 0.3);
    border-color: #8B5CF6;
    color: #FFFFFF !important;
}

/* Hero Banner */
.hero-banner {
    background: linear-gradient(135deg, rgba(79, 70, 229, 0.25) 0%, rgba(139, 92, 246, 0.3) 50%, rgba(236, 72, 153, 0.2) 100%),
                #111827;
    border: 1px solid rgba(139, 92, 246, 0.4);
    border-radius: 20px;
    padding: 35px 40px;
    margin-bottom: 28px;
    box-shadow: 0 10px 35px rgba(0, 0, 0, 0.5);
}
.hero-title {
    font-size: 2.6rem !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #FFFFFF 20%, #C4B5FD 70%, #38BDF8 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    margin: 0 0 10px 0 !important;
}
.hero-subtitle {
    font-size: 1.1rem !important;
    color: #CBD5E1 !important;
    max-width: 800px;
    line-height: 1.6 !important;
    margin: 0 !important;
}

/* Primary Streamlit Buttons */
.stButton > button {
    background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    padding: 8px 24px !important;
    box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4) !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 22px rgba(139, 92, 246, 0.6) !important;
}

/* Slider Customization */
div[data-testid="stSlider"] div[data-baseweb="slider"] {
    color: #8B5CF6 !important;
}

/* Dataframe styling */
div[data-testid="stDataFrame"] {
    background-color: #121829 !important;
    border-radius: 10px !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
}
</style>
"""
