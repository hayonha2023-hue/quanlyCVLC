"""Shared responsive shell; no fixed heights or hidden scrolling."""
import re
import streamlit as st

def apply_theme(dark=False, background=''):
    bg,card,text,muted,border = ('#101827','#182235','#f1f5f9','#b4c1d5','#334155') if dark else ('#f4f7fb','#ffffff','#172a43','#53657b','#e1e8f0')
    image = f'background-image:linear-gradient({bg}dd,{bg}dd),url("data:image/jpeg;base64,{background}");background-size:cover;' if background and re.fullmatch(r'[A-Za-z0-9+/=]+',background) else ''
    st.markdown(f'''<style>
    :root {{ --htcv-card:{card}; --htcv-text:{text}; }}
    [data-testid="stMainBlockContainer"] {{max-width:1180px;}}
    [data-testid="stSidebar"] {{box-shadow:4px 0 24px #10284606;}}
    [data-testid="stExpander"] {{border:1px solid {border};border-radius:12px;background:{card};}}
    [data-testid="stExpander"] summary {{min-height:48px;}}
    [data-testid="stVerticalBlockBorderWrapper"] {{border-color:{border};box-shadow:0 3px 14px #10284605;}}
    .stButton button {{transition:background .15s,border-color .15s;}}
    .stButton button:hover {{border-color:#487fc0;}}
    button:focus-visible,input:focus-visible,textarea:focus-visible {{outline:3px solid #609ee5!important;outline-offset:2px;}}
    [data-testid="stImage"] img {{max-width:100%;height:auto;}}
    .htcv-hero {{padding:1.6rem 1.8rem;border-radius:20px;background:linear-gradient(120deg,#17375c,#226591);margin-bottom:1.5rem;}}
    .htcv-hero h2,.htcv-hero p {{color:white!important;margin:.15rem 0;}}
    .htcv-hero p {{opacity:.9;}}
    @media(max-width:700px) {{
      [data-testid="stHorizontalBlock"] {{flex-wrap:wrap;}}
      [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {{width:100%!important;flex:1 1 100%!important;min-width:0!important;}}
      .htcv-hero {{padding:1.15rem;border-radius:14px;}}
      h1 {{font-size:1.6rem!important;}}
    }}
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
    if st.session_state.get('user'):
        from services.workspace_theme import apply_workspace_theme
        apply_workspace_theme(dark)
