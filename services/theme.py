"""Shared responsive shell; no fixed heights or hidden scrolling."""
import re
import streamlit as st

def apply_theme(dark=False, background=''):
    bg,card,text,muted,border = ('#101827','#182235','#f1f5f9','#b4c1d5','#334155') if dark else ('#f5f7fb','#ffffff','#18263b','#465870','#d6deea')
    image = f'background-image:linear-gradient({bg}dd,{bg}dd),url("data:image/jpeg;base64,{background}");background-size:cover;' if background and re.fullmatch(r'[A-Za-z0-9+/=]+',background) else ''
    st.markdown(f'''<style>
    .stApp {{background:{bg};color:{text};{image}}}
    [data-testid="stHeader"] {{background:{bg};}}
    [data-testid="stSidebar"] {{background:{card};border-right:1px solid {border};}}
    .block-container {{max-width:1280px;padding-top:2.5rem;padding-bottom:3rem;}}
    [data-testid="stSidebar"] .block-container {{padding-top:1rem;}}
    [data-testid="stSidebar"] [role="radiogroup"] {{gap:.4rem;}}
    [data-testid="stSidebar"] [role="radiogroup"] label {{padding:.65rem .8rem;border-radius:10px;border:1px solid transparent;min-height:46px;}}
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {{background:#e7effd;border-color:#a9c5ef;}}
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p {{color:#164b91!important;font-weight:700;}}
    [data-testid="stVerticalBlockBorderWrapper"] {{background:{card};border-radius:14px;}}
    [data-testid="stDataFrame"] {{border:1px solid {border};border-radius:10px;}}
    h1 {{font-size:2rem!important;letter-spacing:-.025em;}}
    h2 {{font-size:1.5rem!important;}}
    h3 {{font-size:1.12rem!important;}}
    p,label {{font-size:1rem;line-height:1.6;}}
    [data-baseweb="input"],[data-baseweb="textarea"],[data-baseweb="select"]>div {{border:1px solid {border}!important;border-radius:8px;}}
    button[kind="secondary"] {{background:{card};border:1px solid {border};color:{text};}}
    [data-testid="stFileUploaderDropzone"] {{background:{card};border:2px dashed {border};}}
    h1,h2,h3,h4,h5,h6,p,label,[data-testid="stMarkdownContainer"], [data-testid="stWidgetLabel"] {{color:{text};}}
    [data-testid="stCaptionContainer"] p {{color:{muted};}}
    [data-testid="stForm"],.html-card {{background:{card};border:1px solid {border};border-radius:16px;padding:1.2rem;}}
    [data-testid="stMetric"] {{background:{card};border:1px solid {border};border-radius:14px;padding:1rem;}}
    .stButton button,.stFormSubmitButton button {{min-height:44px;border-radius:10px;}}
    button[kind="primary"] {{background:#1769d2;color:white;}}
    button[kind="primary"] p {{color:white!important;}}
    input,textarea,[data-baseweb="select"]>div {{background:{card}!important;color:{text}!important;}}
    [data-testid="stTabs"] button p,[data-testid="stExpander"] summary p {{color:{text};}}
    .stTabs [data-baseweb="tab-list"] {{overflow-x:auto;gap:1rem;}}
    .schedule-card .shift-row,.schedule-card b {{color:#172b45;}}
    .htcv-brand {{font-size:1.5rem;font-weight:800;letter-spacing:.03em;color:#1769d2;}}
    .htcv-subtitle {{font-size:.9rem;color:{muted};margin-bottom:1.5rem;}}
    @media(max-width:700px) {{.block-container {{padding:1rem .75rem 2rem;}} h1 {{font-size:1.6rem;}} .stButton button {{min-height:48px;}}}}
    </style>''',unsafe_allow_html=True)
