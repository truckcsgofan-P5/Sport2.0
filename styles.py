import streamlit as st


def apply_styles():
    """Jednotný prémiový DarkGreen vzhled Sport2.0."""
    bg = "#050B08"
    panel = "#0B1510"
    panel2 = "#101F16"
    text = "#F2F8F3"
    muted = "#91A99A"
    border = "rgba(125, 185, 145, .16)"
    accent = "#56F28F"
    accent_dark = "#173D27"

    st.markdown(f"""
    <style>
    :root {{
        color-scheme: dark;
        --ss-bg: {bg};
        --ss-panel: {panel};
        --ss-panel-2: {panel2};
        --ss-text: {text};
        --ss-muted: {muted};
        --ss-border: {border};
        --ss-accent: {accent};
    }}
    .stApp {{
        background:
            radial-gradient(ellipse at 88% 0%, rgba(49, 190, 100, .13), transparent 34%),
            radial-gradient(ellipse at 0% 35%, rgba(32, 105, 61, .08), transparent 32%),
            {bg};
        color: {text};
    }}
    [data-testid="stHeader"] {{ background: rgba(5, 11, 8, .72); }}
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #0B1710 0%, #07100B 100%);
        border-right: 1px solid {border};
    }}
    [data-testid="stSidebar"] > div:first-child {{ padding-top: 1.25rem; }}
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{ color: {muted}; }}
    [data-testid="stSidebar"] [role="radiogroup"] {{ gap: .35rem; }}
    [data-testid="stSidebar"] [role="radiogroup"] label {{
        border-radius: 10px;
        padding: .48rem .65rem;
        transition: background .18s ease;
    }}
    [data-testid="stSidebar"] [role="radiogroup"] label:hover {{
        background: rgba(86, 242, 143, .08);
    }}
    .block-container {{ padding-top: 2rem; padding-bottom: 3rem; max-width: 1540px; }}
    h1, h2, h3 {{ letter-spacing: -.04em; color: {text}; }}
    h1 {{ font-weight: 850 !important; letter-spacing: -.055em; }}
    h2 {{ font-weight: 760 !important; }}
    h3 {{ font-weight: 700 !important; }}
    p, label, [data-testid="stCaptionContainer"] {{ color: {muted}; }}
    .eyebrow {{
        color: {accent}; font-size: .7rem; letter-spacing: .2em;
        font-weight: 850; text-transform: uppercase; margin-bottom: .35rem;
    }}
    .ss-hero {{
        position: relative; overflow: hidden; padding: 1.65rem 1.8rem;
        border: 1px solid rgba(86, 242, 143, .22); border-radius: 22px;
        background: linear-gradient(115deg, rgba(19, 54, 32, .94), rgba(9, 22, 14, .94) 62%, rgba(14, 39, 23, .9));
        box-shadow: 0 18px 55px rgba(0, 0, 0, .22);
        margin: .25rem 0 1.25rem;
    }}
    .ss-hero:after {{
        content: ""; position: absolute; width: 260px; height: 260px; right: -70px; top: -130px;
        border: 1px solid rgba(86, 242, 143, .18); border-radius: 50%;
        box-shadow: 0 0 0 28px rgba(86,242,143,.025), 0 0 0 58px rgba(86,242,143,.02);
    }}
    .ss-hero-kicker {{ color: {accent}; font-size: .68rem; font-weight: 850; letter-spacing: .2em; }}
    .ss-hero-title {{ color: {text}; font-size: clamp(1.65rem, 3vw, 2.45rem); font-weight: 900; letter-spacing: -.06em; margin: .35rem 0; }}
    .ss-hero-copy {{ color: #B4C9BA; font-size: .94rem; margin: 0; max-width: 680px; }}
    [data-testid="stMetric"] {{
        background: linear-gradient(145deg, rgba(17, 37, 25, .98), rgba(9, 20, 13, .98));
        padding: 1.05rem 1.15rem; border: 1px solid {border}; border-radius: 17px;
        box-shadow: 0 10px 28px rgba(0,0,0,.13); min-height: 116px;
    }}
    [data-testid="stMetricLabel"] {{ color: {muted}; font-weight: 700; font-size: .78rem; }}
    [data-testid="stMetricValue"] {{ color: {text}; font-weight: 850; letter-spacing: -.04em; }}
    [data-testid="stMetricDelta"] {{ font-size: .76rem; }}
    div[data-testid="stDataFrame"], div[data-testid="stTable"] {{
        border: 1px solid {border}; border-radius: 14px; overflow: hidden;
        background: rgba(10, 22, 14, .72);
    }}
    div[data-testid="stPlotlyChart"] {{
        background: linear-gradient(145deg, rgba(15, 32, 21, .96), rgba(8, 18, 12, .96));
        border: 1px solid {border}; border-radius: 17px; padding: 8px;
    }}
    div[data-testid="stForm"], [data-testid="stExpander"] {{
        border-color: {border} !important; border-radius: 15px !important;
        background: rgba(10, 22, 14, .45);
    }}
    .stTextInput input, .stNumberInput input, .stDateInput input,
    .stSelectbox [data-baseweb="select"], .stMultiSelect [data-baseweb="select"] {{
        background: #0B1911; border-color: {border}; border-radius: 10px;
    }}
    .stButton > button, .stFormSubmitButton > button {{
        border-radius: 11px; min-height: 2.55rem; font-weight: 750;
        border: 1px solid {border}; transition: all .18s ease;
    }}
    .stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {{
        background: linear-gradient(135deg, {accent}, #32C96E);
        color: #06110A; border: 0; font-weight: 850;
        box-shadow: 0 7px 22px rgba(56, 220, 112, .16);
    }}
    .stButton > button:hover, .stFormSubmitButton > button:hover {{
        border-color: {accent}; transform: translateY(-1px);
    }}
    [data-testid="stTabs"] button {{ font-weight: 700; }}
    .ss-section-head {{ display:flex; align-items:center; gap:.7rem; margin:1.35rem 0 .75rem; }}
    .ss-section-mark {{ width:4px; height:25px; border-radius:5px; background:{accent}; box-shadow:0 0 15px rgba(86,242,143,.45); }}
    .ss-section-title {{ color:{text}; font-size:1.12rem; font-weight:850; letter-spacing:-.025em; }}
    .ss-section-sub {{ color:{muted}; font-size:.78rem; margin-top:.12rem; }}
    .ss-mini-card {{ background:linear-gradient(145deg, rgba(17,39,25,.94), rgba(8,19,12,.96)); border:1px solid {border}; border-radius:15px; padding:1rem 1.1rem; min-height:88px; }}
    .ss-metrics-grid {{
        display: grid; grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: .85rem; margin: .8rem 0 1.25rem;
    }}
    .ss-metric-card {{
        min-width: 0; min-height: 112px; padding: 1rem 1.1rem;
        border: 1px solid {border}; border-radius: 17px;
        background: linear-gradient(145deg, rgba(17, 37, 25, .98), rgba(9, 20, 13, .98));
        box-shadow: 0 10px 28px rgba(0,0,0,.13);
    }}
    .ss-metric-label {{ color: {muted}; font-size: .82rem; font-weight: 700; }}
    .ss-metric-value {{ color: {text}; font-size: 2rem; line-height: 1.2; font-weight: 850; letter-spacing: -.04em; margin-top: .35rem; }}
    .ss-metric-note {{ color: {accent}; font-size: .72rem; margin-top: .2rem; }}
    .ss-mini-label {{ color:{muted}; font-size:.72rem; font-weight:750; text-transform:uppercase; letter-spacing:.08em; }}
    .ss-mini-value {{ color:{text}; font-size:1.22rem; font-weight:850; margin-top:.28rem; }}
    .ss-mini-note {{ color:{accent}; font-size:.74rem; margin-top:.15rem; }}
    .ss-divider {{ height:1px; background:linear-gradient(90deg, rgba(86,242,143,.38), rgba(125,185,145,.04)); margin:1.25rem 0; }}
    [data-testid="stAlert"] {{ border-radius:13px; }}
    [data-testid="stSelectbox"] label, [data-testid="stTextInput"] label, [data-testid="stNumberInput"] label {{ font-weight:700; }}

    hr {{ border-color: {border}; }}
    a {{ color: {accent} !important; }}
    .login-wrap {{ text-align:center; padding: 3rem 0 1.5rem; }}
    .login-wrap h1 {{ font-size: 2.7rem; margin: .3rem 0; }}
    .login-wrap h1 span {{ color:{accent}; }}
    .login-wrap p {{ color:{muted}; }}
    @media (max-width: 700px) {{
        .block-container {{ padding-left: .85rem; padding-right: .85rem; padding-top: 5rem !important; }}
        .ss-hero {{ padding: 1.05rem; border-radius: 16px; margin-bottom: .8rem; }}
        .ss-hero-kicker {{ font-size: .58rem; letter-spacing: .14em; }}
        .ss-hero-title {{ font-size: 1.55rem; margin: .25rem 0; }}
        .ss-hero-copy {{ font-size: .82rem; line-height: 1.45; }}
        .ss-metrics-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .6rem; margin: .65rem 0 1rem; }}
        .ss-metric-card {{ min-height: 86px; padding: .72rem .8rem; border-radius: 13px; }}
        .ss-metric-label {{ font-size: .7rem; }}
        .ss-metric-value {{ font-size: 1.55rem; }}

        [data-testid="stHorizontalBlock"] {{
            flex-direction: row !important;
            flex-wrap: wrap !important;
            gap: .55rem !important;
        }}
        [data-testid="stHorizontalBlock"] > [data-testid="column"] {{
            flex: 1 1 calc(50% - .55rem) !important;
            min-width: calc(50% - .55rem) !important;
            width: calc(50% - .55rem) !important;
        }}
        [data-testid="stMetric"] {{
            min-height: 0; padding: .72rem .8rem; border-radius: 13px;
        }}
        [data-testid="stMetricLabel"] {{ font-size: .7rem; }}
        [data-testid="stMetricValue"] {{ font-size: 1.55rem; }}
        [data-testid="stMetricDelta"] {{ font-size: .68rem; }}
        h2 {{ font-size: 1.25rem !important; }}
        h3 {{ font-size: 1.05rem !important; }}
    }}
    </style>
    """, unsafe_allow_html=True)
