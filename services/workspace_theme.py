"""Theme overrides for the signed-in workspace; supports both Streamlit input renderers."""
import streamlit as st


def apply_workspace_theme(dark=False):
    card, ink, muted, line, soft = ('#18283b','#e9f1fa','#aebfd4','#31455d','#1f344c') if dark else ('#ffffff','#203750','#677c94','#e2e9f1','#f4f7fb')
    st.markdown(f'''<style>
    :root {{--workspace-card:{card};--workspace-ink:{ink};--workspace-muted:{muted};--workspace-line:{line};--workspace-soft:{soft};}}
    [data-testid="stMainBlockContainer"] {{max-width:1250px!important;padding:2.7rem 2.4rem 3rem;}}
    [data-testid="stSidebar"] {{background:{card};border-right:1px solid {line};box-shadow:none;}}
    [data-testid="stSidebarUserContent"] {{padding:1.5rem 1.15rem;}}
    .workspace-brand {{display:flex;gap:11px;align-items:center;margin:0 0 26px;}}
    .workspace-logo {{display:grid;place-items:center;background:#1b426c;color:#fff;width:41px;height:41px;border-radius:12px;font-size:24px;font-weight:800;}}
    .workspace-brand strong {{display:block;letter-spacing:.04em;font-size:22px;line-height:1.3;color:{ink};}}
    .workspace-brand small {{display:block;font-size:9px;font-weight:650;letter-spacing:.09em;color:{muted};margin-top:3px;}}
    .workspace-account {{display:flex;gap:11px;align-items:center;padding:12px;border:1px solid {line};border-radius:13px;margin-bottom:5px;background:{soft};}}
    .workspace-avatar {{display:grid;place-items:center;flex:0 0 34px;height:34px;background:#dceaf7;color:#285881;border-radius:50%;font-size:15px;font-weight:700;}}
    .workspace-account strong {{display:block;font-size:13px;color:{ink};overflow-wrap:anywhere;}}
    .workspace-account small {{display:block;font-size:11px;color:{muted};margin-top:2px;}}
    .workspace-menu-label {{font-size:10px;font-weight:700;letter-spacing:.13em;color:{muted};margin:8px 0 2px;}}
    [data-testid="stSidebar"] .stButton button {{min-height:42px;font-size:13px;border-radius:10px;}}
    [data-testid="stSidebar"] .stButton button p {{font-size:13px;}}
    .st-key-workspace_navigation .stButton button {{justify-content:flex-start;border-color:transparent;background:transparent;box-shadow:none;padding:.55rem .8rem;}}
    .st-key-workspace_navigation .stButton button:hover {{background:{soft};border-color:{line};}}
    .st-key-workspace_navigation button[kind="primary"] {{background:#1e4d7b!important;border-color:#1e4d7b!important;box-shadow:0 4px 12px #133e6315;}}
    .st-key-workspace_navigation button[kind="primary"] p {{color:white!important;font-weight:650;}}
    .st-key-workspace_navigation [data-testid="stVerticalBlock"] {{gap:.35rem;}}
    .st-key-workspace_navigation [data-testid="stExpander"] {{margin-top:9px;}}
    [data-testid="stSidebar"] [data-testid="stExpander"] details {{border:1px solid {line};background:transparent;border-radius:11px;}}
    [data-testid="stSidebar"] [data-testid="stExpander"] summary p {{font-size:13px;font-weight:600;}}
    .workspace-context {{display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap;font-size:11px;color:{muted};padding-bottom:13px;border-bottom:1px solid {line};margin-bottom:2px;}}
    .workspace-context strong {{font-size:12px;font-weight:600;color:{ink};margin-left:7px;}}
    .workspace-sync {{display:flex;align-items:center;gap:6px;}}
    .workspace-sync::before {{content:"";width:6px;height:6px;border-radius:50%;background:#be8a35;}}
    .workspace-sync.ready::before {{background:#459780;}}
    .workspace-page-heading {{margin:8px 0 13px;}}
    .workspace-eyebrow {{color:{muted};font-size:10px;letter-spacing:.15em;font-weight:700;margin-bottom:8px;}}
    .workspace-page-heading h1 {{font-size:29px!important;font-weight:750;letter-spacing:-.035em;line-height:1.3;margin:0 0 9px;padding:0;color:{ink};}}
    .workspace-page-heading p {{font-size:14px;line-height:1.65;color:{muted};margin:0;}}
    .workspace-welcome {{position:relative;border-radius:20px;padding:27px 30px;background:linear-gradient(110deg,#173656,#235982);margin:5px 0 9px;}}
    .workspace-welcome .workspace-eyebrow {{color:#aecfe7;margin-bottom:10px;}}
    .workspace-welcome h1 {{color:white!important;font-size:30px!important;line-height:1.3;letter-spacing:-.035em;margin:0 0 9px;padding:0;}}
    .workspace-welcome p {{color:#c8dcee!important;font-size:14px;margin:0;line-height:1.6;}}
    .workspace-welcome .workspace-date {{font-size:11px;color:#b6d2e6;margin-top:20px;}}
    [data-testid="stMetric"] {{border:1px solid {line};border-radius:15px;padding:18px 20px;background:{card};box-shadow:0 3px 12px #132c4603;}}
    [data-testid="stMetricLabel"] p {{font-size:12px!important;font-weight:500;color:{muted};}}
    [data-testid="stMetricValue"] {{font-size:29px!important;letter-spacing:-.04em;color:{ink};}}
    [data-testid="stVerticalBlockBorderWrapper"] {{border-color:{line};}}
    .st-key-workspace_report,.st-key-workspace_active_tool {{background:{card};border-color:{line};border-radius:15px;}}
    .workspace-section-title {{font-size:17px;font-weight:700;color:{ink};margin:12px 0 3px;letter-spacing:-.02em;}}
    .workspace-section-note {{font-size:12px;color:{muted};margin-bottom:12px;}}
    .workspace-tool-card {{min-height:160px;}}
    .workspace-tool-number {{width:35px;height:35px;border-radius:10px;display:grid;place-items:center;background:#eaf2fb;color:#275c90;font-size:12px;font-weight:700;margin-bottom:16px;}}
    .workspace-tool-card h3 {{font-size:17px!important;line-height:1.4;margin:0 0 8px;padding:0;color:{ink};}}
    .workspace-tool-card p {{color:{muted};font-size:13px;line-height:1.65;margin:0 0 5px;}}
    .st-key-overview_tools [data-testid="stVerticalBlockBorderWrapper"] {{background:{card};border-color:{line};border-radius:17px;box-shadow:0 6px 20px #15355604;}}
    .st-key-overview_tools .stButton button {{justify-content:space-between;background:{soft};color:{ink};border:1px solid {line};}}
    .st-key-overview_tools .stButton button:hover {{border-color:#739ac4;background:{card};}}
    .workspace-steps {{display:flex;gap:12px;margin:1px 0 16px;flex-wrap:wrap;}}
    .workspace-steps > div {{display:flex;align-items:center;gap:9px;padding:9px 13px;border:1px solid {line};background:{card};border-radius:10px;font-size:12px;color:{muted};}}
    .workspace-steps span {{font-weight:700;color:#5990c1;font-size:11px;}}
    [data-testid="stTextInputRootElement"],[data-testid="stTextAreaRootElement"], [data-baseweb="input"],[data-baseweb="textarea"] {{border:1px solid {line}!important;background:{card};border-radius:10px;min-height:46px;}}
    [data-testid="stTextInputRootElement"]:focus-within,[data-testid="stTextAreaRootElement"]:focus-within {{border-color:#578fbe!important;box-shadow:0 0 0 3px #367bbe12;}}
    [data-testid="stSelectbox"] [data-baseweb="select"]>div,[data-testid="stMultiSelect"] [data-baseweb="select"]>div {{min-height:46px;border-radius:10px;}}
    [data-testid="stWidgetLabel"] p {{font-size:13px;color:{ink};font-weight:550;}}
    input,textarea {{font-size:16px!important;}}
    h2 {{font-size:21px!important;letter-spacing:-.02em;}}
    h3 {{font-size:17px!important;letter-spacing:-.01em;}}
    .stButton button,.stDownloadButton button,.stFormSubmitButton button {{min-height:44px;border-radius:10px;transition:background .15s,border-color .15s;}}
    button[kind="primary"] {{background:#215d96;border:1px solid #215d96;}}
    button[kind="primary"]:hover {{background:#194c7d;border-color:#194c7d;}}
    [data-testid="stFileUploaderDropzone"] {{padding:24px;border:1px dashed #8eabc6;background:{soft};border-radius:13px;}}
    [data-testid="stFileUploaderDropzone"] p {{font-size:14px;}}
    [data-testid="stExpander"] {{border:0;background:transparent;box-shadow:none;}}
    [data-testid="stExpander"] details {{background:{card};border:1px solid {line};border-radius:13px;}}
    [data-testid="stExpander"] summary {{min-height:46px;}}
    [data-testid="stExpander"] summary p {{font-size:13px;}}
    [data-testid="stDataFrame"] {{background:{card};border:1px solid {line};border-radius:12px;}}
    [data-testid="stTabs"] [role="tablist"] {{border-bottom:1px solid {line};gap:22px;}}
    [data-testid="stTabs"] button[role="tab"] {{min-height:43px;}}
    [data-testid="stTabs"] button[aria-selected="true"] p {{color:#4785bb;font-weight:650;}}
    [data-testid="stAlert"] {{border-radius:11px;}}
    [data-testid="stAlert"] p {{font-size:13px;line-height:1.6;}}
    .st-key-workspace_mobile_navigation {{display:none;}}
    @media(max-width:900px) {{
      [data-testid="stMainBlockContainer"] {{padding:2.5rem 1.2rem 2rem;}}
      .workspace-tool-card {{min-height:185px;}}
    }}
    @media(max-width:700px) {{
      [data-testid="stMainBlockContainer"] {{padding:3.3rem 1rem 2rem;}}
      .st-key-workspace_mobile_navigation {{display:block;margin-bottom:6px;}}
      .workspace-context {{gap:7px;padding-bottom:12px;}}
      .workspace-context strong {{margin-left:4px;}}
      .workspace-welcome {{padding:23px 21px;border-radius:16px;}}
      .workspace-welcome h1 {{font-size:25px!important;}}
      .workspace-welcome p {{font-size:13px;}}
      .workspace-page-heading h1 {{font-size:25px!important;}}
      .workspace-page-heading p {{font-size:13px;}}
      .workspace-tool-card {{min-height:0;}}
      .workspace-tool-number {{float:right;margin:0 0 12px 12px;}}
      .workspace-tool-card p {{margin-bottom:12px;}}
      .st-key-overview_metrics [data-testid="stHorizontalBlock"] {{gap:9px;flex-wrap:nowrap;}}
      .st-key-overview_metrics [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {{width:auto!important;flex:1 1 0!important;min-width:0!important;}}
      .st-key-overview_metrics [data-testid="stMetric"] {{padding:12px 9px;border-radius:11px;}}
      .st-key-overview_metrics [data-testid="stMetricValue"] {{font-size:24px!important;}}
      .st-key-overview_metrics [data-testid="stMetricLabel"] p {{font-size:11px!important;white-space:normal;}}
      .workspace-steps {{gap:6px;}}
      .workspace-steps > div {{padding:7px 9px;font-size:11px;gap:6px;}}
      .stButton button,.stDownloadButton button {{min-height:46px;}}
    }}
    @media(prefers-reduced-motion:reduce) {{.stButton button,.stDownloadButton button {{transition:none;}}}}
    </style>''', unsafe_allow_html=True)
