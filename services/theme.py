"""One shared visual system for forms, tables, reports and administration."""
import re
import streamlit as st


def apply_theme(dark=False, background=''):
    bg, card, ink, muted, line, soft, accent = (
        ('#101b28','#192838','#edf2f8','#a6b7c9','#344759','#223448','#91bdea') if dark else
        ('#f3f5f8','#ffffff','#203149','#66778a','#dae2eb','#edf3f9','#214e78'))
    backdrop = f'background-image:linear-gradient({bg}ed,{bg}ed),url("data:image/jpeg;base64,{background}");background-size:cover;background-attachment:fixed;' if background and re.fullmatch(r'[A-Za-z0-9+/=]+',background) else ''
    st.markdown(f"""<style>
    :root {{--htcv-card:{card};--htcv-text:{ink};--ink:{ink};--muted:{muted};--line:{line};--soft:{soft};--accent:{accent};}}
    .stApp {{background:{bg};color:{ink};{backdrop}}}
    [data-testid="stHeader"] {{background:{bg};}}
    [data-testid="stMainBlockContainer"] {{max-width:1200px;padding:2.4rem 2rem 3rem;}}
    [data-testid="stSidebar"] {{background:{card};border-right:1px solid {line};box-shadow:none;}}
    [data-testid="stSidebarUserContent"] {{padding:1.5rem 1rem;}}
    h1,h2,h3,h4,h5,h6,p,label,[data-testid="stMarkdownContainer"] {{color:{ink};}}
    h1 {{font-size:28px!important;letter-spacing:-.03em;}}
    h2 {{font-size:21px!important;}} h3 {{font-size:17px!important;}}
    p,label {{font-size:16px;line-height:1.6;}}
    [data-testid="stCaptionContainer"] p {{color:{muted};font-size:14px;}}
    [data-testid="stWidgetLabel"] p {{font-size:15px;font-weight:600;}}
    [data-testid="stTextInputRootElement"],[data-testid="stTextAreaRootElement"],[data-baseweb="input"],[data-baseweb="textarea"],[data-baseweb="select"]>div {{background:{card};border:1px solid {line}!important;border-radius:7px;min-height:48px;}}
    input,textarea {{font-size:16px!important;background:{card}!important;color:{ink}!important;}}
    [data-baseweb="select"]>div {{color:{ink};}}
    button:focus-visible,input:focus-visible,textarea:focus-visible {{outline:3px solid #75a9d4!important;outline-offset:2px;}}
    .stButton button,.stDownloadButton button,.stFormSubmitButton button,.stLinkButton a {{min-height:48px;border-radius:7px;}}
    button[kind="secondary"],button[kind="secondaryFormSubmit"] {{background:{card};border:1px solid {line};color:{ink};}}
    button[kind="primary"],button[kind="primaryFormSubmit"] {{background:#214e78;border:1px solid #214e78;color:#fff;}}
    button[kind="primary"] p,button[kind="primaryFormSubmit"] p {{color:#fff!important;}}
    button:disabled {{opacity:.55;}}
    [data-testid="stForm"],[data-testid="stVerticalBlockBorderWrapper"] {{border-color:{line};border-radius:9px;background:{card};box-shadow:none;}}
    [data-testid="stForm"] {{padding:20px;}}
    [data-testid="stExpander"] {{background:transparent;border:0;}}
    [data-testid="stExpander"] details {{border:1px solid {line};border-radius:8px;background:{card};}}
    [data-testid="stExpander"] summary {{min-height:48px;}}
    [data-testid="stExpander"] summary p {{font-size:15px;color:{ink};}}
    [data-testid="stMetric"] {{background:{card};border:1px solid {line};border-radius:8px;padding:14px 16px;}}
    [data-testid="stMetricLabel"] p {{color:{muted};font-size:14px;}}
    [data-testid="stMetricValue"] {{color:{ink};font-size:26px!important;}}
    [data-testid="stDataFrame"] {{border:1px solid {line};border-radius:8px;overflow:hidden;}}
    [data-testid="stFileUploaderDropzone"] {{background:{soft};border:1px dashed #96acc1;border-radius:8px;padding:24px;}}
    [data-testid="stTabs"] [role="tablist"] {{gap:22px;overflow-x:auto;border-bottom:1px solid {line};}}
    [data-testid="stTabs"] [role="tab"] {{min-height:48px;white-space:nowrap;}}
    [data-testid="stTabs"] [role="tab"] p {{color:{muted};font-size:15px;}}
    [data-testid="stTabs"] [aria-selected="true"] p {{color:{accent};font-weight:650;}}
    [data-testid="stAlert"] {{border-radius:8px;}} [data-testid="stAlert"] p {{font-size:15px;}}
    [data-testid="stImage"] img {{max-width:100%;height:auto;}}
    hr {{border-color:{line};}}
    .record-grid {{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr));gap:12px;margin:12px 0 20px;}}
    .record-card {{padding:18px;border:1px solid {line};border-radius:9px;background:{card};}}
    .record-card h3 {{margin:0 0 12px;padding:0;font-size:18px!important;overflow-wrap:anywhere;}}
    .record-field {{padding:9px 0;border-top:1px solid {line};}}
    .record-field span {{display:block;font-size:13px;color:{muted};margin-bottom:4px;}}
    .record-field strong {{font-size:16px;font-weight:600;line-height:1.6;color:{ink};overflow-wrap:anywhere;}}
    [data-testid="stNumberInput"] input {{font-variant-numeric:tabular-nums;}}
    [data-testid="stForm"] .stFormSubmitButton {{margin-top:12px;}}
    [data-testid="stChatMessage"] {{border:1px solid {line};border-radius:9px;}}
    [data-testid="stTabs"] button[aria-selected="true"] {{background:{soft};border-radius:6px;}}

    .workspace-empty {{padding:32px 20px;border:1px dashed {line};border-radius:8px;text-align:center;background:{card};}}
    .workspace-empty strong {{display:block;color:{ink};font-size:15px;margin-bottom:6px;}}
    .workspace-empty p {{color:{muted};font-size:15px;margin:0;}}
    @media(max-width:700px) {{
      [data-testid="stMainBlockContainer"] {{padding:3.5rem 1rem 2rem;}}
      [data-testid="stHorizontalBlock"] {{flex-wrap:wrap;}}
      [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {{width:100%!important;flex:1 1 100%!important;min-width:0!important;}}
      h1 {{font-size:24px!important;}}
      [data-testid="stTabs"] [role="tablist"] {{flex-wrap:wrap;height:auto;gap:6px;overflow:visible;}}
      [data-testid="stTabs"] [role="tab"] {{padding:8px 12px;height:auto;}}
      [data-baseweb="tab-highlight"],[data-baseweb="tab-border"] {{display:none;}}

      [data-testid="stForm"] {{padding:14px;}}
      .stButton button,.stDownloadButton button,.stFormSubmitButton button {{min-height:48px;}}
    }}
    @media(prefers-reduced-motion:reduce) {{* {{scroll-behavior:auto!important;transition:none!important;}}}}
    </style>""",unsafe_allow_html=True)
    if st.session_state.get('user'):
        from services.workspace_theme import apply_workspace_theme
        apply_workspace_theme(dark)
