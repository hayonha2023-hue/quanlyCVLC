"""Presentation of saved targets. No calculations or data writes."""
from decimal import Decimal
from html import escape
import re
import streamlit as st
from services.app_data import number

CSS='''<style>
.target-cards {display:grid;gap:14px;margin:12px 0 20px;}
.target-card {background:var(--htcv-card);border:1px solid var(--line);border-radius:9px;overflow:hidden;}
.target-card-head {padding:14px 16px;border-bottom:1px solid var(--line);color:var(--ink);font-size:17px;font-weight:700;}
.target-card-head small {display:block;font-size:12px;font-weight:400;color:var(--muted);margin-top:4px;}
.target-values {display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));}
.target-value {padding:18px 16px;border-right:1px solid var(--line);min-width:0;}
.target-value:last-child {border-right:0;}
.target-value span {display:block;color:var(--muted);font-size:13px;font-weight:550;margin-bottom:8px;}
.target-value strong {display:block;color:var(--ink);font-size:clamp(22px,2.4vw,32px);font-weight:750;font-variant-numeric:tabular-nums;line-height:1.25;overflow-wrap:anywhere;}
.target-value.goal {border-top:3px solid #5185bd;}
.target-value.done {border-top:3px solid #47917a;}
.target-value.remaining {border-top:3px solid #bd862e;}
.target-value.neutral {border-top:3px solid var(--line);}
@media(max-width:700px) {
.target-values {grid-template-columns:repeat(2,minmax(0,1fr));}
.target-value {padding:14px 12px;border-bottom:1px solid var(--line);}
.target-value strong {font-size:23px;}
.target-value span {font-size:12px;}
.target-card-head {font-size:16px;}
}
@media(max-width:360px) {.target-values {grid-template-columns:1fr;}}
</style>'''


def display_number(value):
    if value is None or str(value).strip()=='': return '—'
    if isinstance(value,str) and not re.fullmatch(r'[+\-]?[\d.,\s]+',value.strip()): return value
    n=Decimal(str(number(value)))
    text=format(n,',f')
    if '.' in text: text=text.rstrip('0').rstrip('.')
    return text.translate(str.maketrans({',':'.','.':','}))


def cards_html(items, columns, unit_by_name=None):
    cards=[]
    for item in items:
        name=str(item.get('Chỉ số',''))
        unit=(unit_by_name or {}).get(name,'')
        note=f'Đơn vị: {unit}' if unit else 'Giữ nguyên đơn vị của bảng gốc'
        cells=[]
        for field,label,tone in columns:
            cells.append(f'<div class="target-value {tone}"><span>{escape(label)}</span><strong>{escape(display_number(item.get(field)))}</strong></div>')
        cards.append(f'<section class="target-card"><div class="target-card-head">{escape(name)}<small>{escape(note)}</small></div><div class="target-values">{"".join(cells)}</div></section>')
    return '<div class="target-cards">'+''.join(cards)+'</div>'


def render_cards(items, columns, units=None):
    if not items: return
    st.markdown(CSS,unsafe_allow_html=True)
    st.markdown(cards_html(items,columns,units),unsafe_allow_html=True)
