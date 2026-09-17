"""Workspace layout; colors and controls belong to the shared theme."""
import streamlit as st


def apply_workspace_theme(dark=False):
    st.markdown("""<style>
    .workspace-brand {display:flex;gap:11px;align-items:center;margin:0 0 22px;}
    .workspace-logo {display:grid;place-items:center;width:38px;height:38px;border-radius:8px;background:#214e78;color:#fff;font-size:24px;font-weight:750;}
    .workspace-brand strong {display:block;color:var(--ink);font-size:22px;line-height:1.2;}
    .workspace-brand small {display:block;color:var(--muted);font-size:11px;margin-top:3px;}
    .workspace-account {display:flex;gap:10px;align-items:center;padding:12px 0;border-bottom:1px solid var(--line);margin-bottom:10px;}
    .workspace-avatar {display:grid;place-items:center;width:32px;height:32px;border-radius:50%;background:var(--soft);color:var(--accent);font-weight:650;}
    .workspace-account strong {display:block;color:var(--ink);font-size:13px;overflow-wrap:anywhere;}
    .workspace-account small {color:var(--muted);font-size:11px;}
    .workspace-menu-label {font-size:10px;letter-spacing:.09em;font-weight:650;color:var(--muted);margin:14px 0 6px;}
    [data-testid="stSidebar"] .stButton button {font-size:13px;}
    .st-key-workspace_navigation .stButton button {justify-content:flex-start;background:transparent;border:1px solid transparent;padding:9px 12px;}
    .st-key-workspace_navigation .stButton button p {font-size:13px;}
    .st-key-workspace_navigation .stButton button:hover {background:var(--soft);}
    .st-key-workspace_navigation button[kind="primary"] {background:var(--soft)!important;border-left:3px solid var(--accent)!important;border-radius:0 7px 7px 0;}
    .st-key-workspace_navigation button[kind="primary"] p {color:var(--accent)!important;font-weight:650;}
    .st-key-workspace_navigation [data-testid="stVerticalBlock"] {gap:4px;}
    .st-key-workspace_navigation [data-testid="stExpander"] {margin-top:10px;}
    .workspace-context {display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;border-bottom:1px solid var(--line);padding:0 0 13px;margin-bottom:4px;color:var(--muted);font-size:12px;}
    .workspace-context strong {color:var(--ink);font-weight:600;margin-left:5px;}
    .workspace-sync {display:flex;align-items:center;gap:6px;}
    .workspace-sync::before {content:"";width:6px;height:6px;border-radius:50%;background:#ba8733;}
    .workspace-sync.ready::before {background:#428674;}
    .workspace-page-heading {margin:6px 0 18px;}
    .workspace-page-heading h1 {padding:0;margin:0 0 7px;font-weight:700;line-height:1.3;}
    .workspace-page-heading p {color:var(--muted);font-size:14px;margin:0;}
    .workspace-section-title {font-size:17px;font-weight:650;color:var(--ink);margin:10px 0;}
    .workspace-steps {display:flex;gap:10px;flex-wrap:wrap;margin:0 0 12px;font-size:12px;color:var(--muted);}
    .workspace-steps span {display:flex;align-items:center;gap:7px;}
    .workspace-steps b {display:grid;place-items:center;width:22px;height:22px;border:1px solid var(--line);border-radius:50%;font-size:11px;font-weight:600;}
    .st-key-overview_tools .stButton button {justify-content:flex-start;min-height:70px;background:var(--htcv-card);border:1px solid var(--line);padding:16px;color:var(--accent);}
    .st-key-overview_tools .stButton button p {font-size:15px;font-weight:600;}
    .st-key-overview_tools .stButton button:hover {border-color:var(--accent);background:var(--soft);}
    .st-key-workspace_mobile_navigation {display:none;}
    @media(max-width:700px) {
      .st-key-workspace_mobile_navigation {display:block;}
      .workspace-context {font-size:11px;gap:5px;}
      .workspace-page-heading {margin-bottom:12px;}
      .st-key-overview_tools [data-testid="stHorizontalBlock"] {gap:8px;}
      .st-key-overview_tools .stButton button {min-height:52px;padding:10px 14px;}
      .st-key-overview_metrics [data-testid="stHorizontalBlock"] {gap:8px;flex-wrap:nowrap;}
      .st-key-overview_metrics [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {width:auto!important;flex:1 1 0!important;min-width:0!important;}
      .st-key-overview_metrics [data-testid="stMetric"] {padding:12px 8px;}
      .st-key-overview_metrics [data-testid="stMetricLabel"] p {font-size:11px;white-space:normal;}
      .st-key-overview_metrics [data-testid="stMetricValue"] {font-size:23px!important;}
      .workspace-steps {gap:8px;font-size:11px;}
    }
    </style>""",unsafe_allow_html=True)
