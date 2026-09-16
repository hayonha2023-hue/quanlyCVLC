"""Shared responsive shell; no fixed heights or hidden scrolling."""
import re
import streamlit as st

def apply_theme(dark=False, background=''):
    bg,card,text,muted,border = ('#101827','#182235','#f1f5f9','#b4c1d5','#334155') if dark else ('#f3f6fb','#ffffff','#172b45','#526780','#dce5f0')
    image = f'background-image:linear-gradient({bg}dd,{bg}dd),url("data:image/jpeg;base64,{background}");background-size:cover;' if background and re.fullmatch(r'[A-Za-z0-9+/=]+',background) else ''
    st.markdown(f'''<style>
    .stApp {{background:{bg};color:{text};{image}}}
    [data-testid="stHeader"] {{background:{bg};}}
    [data-testid="stSidebar"] {{background:{card};border-right:1px solid {border};}}
    .block-container {{max-width:1440px;padding-top:2rem;padding-bottom:3rem;}}
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
