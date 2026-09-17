"""Readable schedule cards shared by published schedules and draft previews."""
from html import escape
import re
import unicodedata
import streamlit as st

BOARD_CSS = '''<style>
.schedule-board {display:grid;gap:16px;margin:8px 0 18px;}
.schedule-day {border:1px solid var(--line);border-radius:10px;overflow:hidden;background:var(--htcv-card);}
.schedule-day-title {display:flex;align-items:center;gap:14px;padding:14px 18px;background:var(--soft);border-bottom:1px solid var(--line);font-size:18px;font-weight:750;color:var(--ink);}
.schedule-date {font-size:27px;letter-spacing:-.035em;font-weight:800;color:var(--accent);line-height:1.2;}
.schedule-weekday {font-size:16px;line-height:1.4;color:var(--ink);}
.schedule-shifts {display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:0;}
.schedule-shift {padding:16px 18px;border-right:1px solid var(--line);min-width:0;}
.schedule-shift:last-child {border-right:0;}
.schedule-shift-title {display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:12px;}
.schedule-shift-title strong {font-size:15px;padding:5px 10px;border-radius:5px;background:#e8eff8;color:#254e80;border-left:4px solid #5283b9;}
.schedule-shift.morning .schedule-shift-title strong {background:#fff2d6;color:#795109;border-color:#c38c23;}
.schedule-shift.afternoon .schedule-shift-title strong {background:#e6effb;color:#24568a;border-color:#4b83c4;}
.schedule-shift.midday .schedule-shift-title strong {background:#eee9fa;color:#65478b;border-color:#8b6db2;}
.schedule-count {font-size:12px;color:var(--muted);white-space:nowrap;}
.schedule-people {display:flex;flex-wrap:wrap;gap:7px;}
.schedule-person {padding:7px 10px;border:1px solid var(--line);border-radius:6px;color:var(--ink);font-size:15px;font-weight:550;line-height:1.5;overflow-wrap:anywhere;max-width:100%;}
.schedule-person.match {background:var(--soft);border:2px solid var(--accent);font-weight:750;}
.schedule-vacant {font-size:13px;color:var(--muted);padding:7px 0;}
@media(max-width:700px) {
.schedule-board {gap:12px;}
.schedule-day-title {padding:12px 14px;font-size:17px;}
.schedule-shifts {grid-template-columns:1fr;}
.schedule-shift {padding:13px 14px;border-right:0;border-bottom:1px solid var(--line);}
.schedule-shift:last-child {border-bottom:0;}
.schedule-shift-title {margin-bottom:9px;}
.schedule-person {font-size:16px;}
}
</style>'''


def people(value):
    if isinstance(value,list):
        return [str(name).strip() for name in value if str(name).strip()]
    if value is None: return []
    return [str(value).strip()] if str(value).strip() else []


def name_key(value):
    text=unicodedata.normalize('NFD',str(value).strip().casefold().replace('đ','d'))
    return ''.join(c for c in text if not unicodedata.combining(c))


def day_heading(day):
    label=str(day)
    match=re.fullmatch(r'(\d{1,2}/\d{1,2}(?:/\d{4})?)\s*[-–·]\s*(.+)',label)
    if not match: return escape(label)
    return f'<span class="schedule-date">{escape(match[1])}</span><span class="schedule-weekday">{escape(match[2])}</span>'


def board_html(history, query=''):
    query=name_key(query)
    days=[]
    for day, shifts in history.items():
        if not isinstance(shifts,dict): continue
        if query and not any(query in name_key(name) for value in shifts.values() for name in people(value)):
            continue
        panels=[]
        ordered=[shift for shift in ['Sáng','10h30','Chiều'] if shift in shifts]
        ordered += [shift for shift in shifts if shift not in ordered]
        for shift in ordered:
            staff=people(shifts[shift])
            color={'Sáng':'morning','Chiều':'afternoon','10h30':'midday'}.get(shift,'other')
            chips=''.join('<span class="schedule-person'+(' match' if query and query in name_key(name) else '')+'">'+escape(name)+'</span>' for name in staff)
            if not chips: chips='<span class="schedule-vacant">Chưa phân công</span>'
            panels.append(f'<section class="schedule-shift {color}"><div class="schedule-shift-title"><strong>Ca {escape(str(shift))}</strong><span class="schedule-count">{len(staff)} người</span></div><div class="schedule-people">{chips}</div></section>')
        if not panels: panels=['<div class="schedule-shift"><span class="schedule-vacant">Chưa có ca làm</span></div>']
        days.append(f'<article class="schedule-day"><div class="schedule-day-title">{day_heading(day)}</div><div class="schedule-shifts">{"".join(panels)}</div></article>')
    return '<div class="schedule-board">'+''.join(days)+'</div>' if days else ''


def render_board(history, query=''):
    st.markdown(BOARD_CSS,unsafe_allow_html=True)
    html=board_html(history,query)
    if html: st.markdown(html,unsafe_allow_html=True)
    else: st.info('Không có lịch phù hợp với tên đang tìm.' if query else 'Chưa có lịch làm việc.')
