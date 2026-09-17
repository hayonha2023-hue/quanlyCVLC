"""Shared readable tables and record summaries; display-only helpers."""
from html import escape
import pandas as pd
import streamlit as st
from views.target_cards import display_number


def readable_dataframe(data, **kwargs):
    frame=data if isinstance(data,pd.DataFrame) else pd.DataFrame(data)
    formatters={col:display_number for col in frame.select_dtypes(include='number').columns}
    styled=frame.style.format(formatters,na_rep='—')
    return st.dataframe(styled,hide_index=True,use_container_width=True,row_height=44,**kwargs)


def record_cards(items, title, fields):
    if not items: return
    chunks=[]
    for item in items:
        values=''.join(f'<div class="record-field"><span>{escape(label)}</span><strong>{escape(str(item.get(key,"—")))}</strong></div>' for key,label in fields)
        chunks.append(f'<article class="record-card"><h3>{escape(str(item.get(title,"")))}</h3>{values}</article>')
    st.markdown('<div class="record-grid">'+''.join(chunks)+'</div>',unsafe_allow_html=True)
