"""Shared presentation and navigation for the authenticated workspace."""
from html import escape

import streamlit as st


LABELS = {
    '🏠 Tổng quan': 'Tổng quan', '⚡ Sắp lịch & Đảo ca': 'Sắp lịch & đảo ca',
    '🔍 Quét AI KPI': 'Quét AI KPI', '✂️ Chia Data': 'Chia data',
    '📋 Xem Lịch': 'Lịch làm việc', '📊 Tích Lũy': 'Tích lũy ca',
    '📈 Theo Dõi KPI': 'KPI tháng', '📊 Target Ngày': 'Target ngày',
    '🛒 Lịch Ecom': 'Lịch Ecom', '💰 Quỹ Shop': 'Quỹ shop',
    '📍 Thị Trường': 'Lịch thị trường', '📞 Danh Bạ': 'Danh bạ',
    '🤖 AI Tư Vấn': 'Tư vấn AI', '👥 Quản Trị Admin': 'Quản trị',
}


ICONS = {
    '🏠 Tổng quan': ':material/home:', '⚡ Sắp lịch & Đảo ca': ':material/calendar_month:',
    '🔍 Quét AI KPI': ':material/document_scanner:', '✂️ Chia Data': ':material/table_view:',
}


def empty_state(title, description):
    st.markdown(f'<div class="workspace-empty"><strong>{escape(title)}</strong><p>{escape(description)}</p></div>', unsafe_allow_html=True)


def navigate(page):
    st.session_state.navigation = page
    st.session_state.show_bg = False
    st.session_state.show_pass = False
    for key in list(st.session_state):
        if str(key).startswith('editing_'):
            st.session_state[key] = False


def sidebar_identity(user, admin=False, super_admin=False):
    role = 'Quản trị hệ thống' if super_admin else ('Quản trị chi nhánh' if admin else 'Nhân viên')
    st.markdown(f'''<div class="workspace-brand"><span class="workspace-logo">H</span>
<div><strong>HTCV</strong><small>Quản lý nội bộ</small></div></div>
<div class="workspace-account"><span class="workspace-avatar">{escape(str(user)[:1].upper())}</span>
<div><strong>{escape(str(user))}</strong><small>{role}</small></div></div>''', unsafe_allow_html=True)


def sidebar_navigation(options, tools):
    if st.session_state.get('navigation') not in options:
        st.session_state.navigation = options[0]
    selected = st.session_state.navigation
    primary = [options[0]] + tools
    with st.container(key='workspace_navigation'):
        st.markdown('<div class="workspace-menu-label">LÀM VIỆC</div>', unsafe_allow_html=True)
        for page in primary:
            st.button(LABELS.get(page, page), icon=ICONS.get(page), key='nav_'+page, type='primary' if selected == page else 'secondary',
                      on_click=navigate, args=(page,), use_container_width=True)
        reports = [page for page in options if page not in primary and page != '👥 Quản Trị Admin']
        with st.expander('Dữ liệu & báo cáo', expanded=selected in reports):
            for page in reports:
                st.button(LABELS.get(page, page), icon=ICONS.get(page), key='nav_'+page, type='primary' if selected == page else 'secondary',
                          on_click=navigate, args=(page,), use_container_width=True)
    return selected


def mobile_navigation(options):
    st.session_state.mobile_destination = st.session_state.navigation
    def change():
        navigate(st.session_state.mobile_destination)
    with st.container(key='workspace_mobile_navigation'):
        st.selectbox('Đi đến chức năng', options, key='mobile_destination', on_change=change, format_func=lambda page: LABELS.get(page, page))


def page_header(title, description, eyebrow='KHÔNG GIAN LÀM VIỆC'):
    st.markdown(f'''<div class="workspace-page-heading">
<h1>{escape(title)}</h1><p>{escape(description)}</p></div>''', unsafe_allow_html=True)


def sync_status():
    shop = escape(str(st.session_state.get('current_shop', '')))
    synced = st.session_state.get('synced_at')
    failed = st.session_state.get('sync_error')
    status = 'Chưa tải được dữ liệu mới' if failed else ('Cập nhật '+str(synced) if synced else 'Chưa tải dữ liệu')
    state = 'stale' if failed or not synced else 'ready'
    st.markdown(f'''<div class="workspace-context"><span>CHI NHÁNH <strong>{shop}</strong></span>
<span class="workspace-sync {state}">{escape(status)}</span></div>''', unsafe_allow_html=True)


def workflow_steps(labels):
    steps = ''.join(f'<span><b>{i}</b>{escape(label)}</span>' for i, label in enumerate(labels, 1))
    st.markdown(f'<div class="workspace-steps">{steps}</div>', unsafe_allow_html=True)
