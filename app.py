import streamlit as st
import requests
import time
import io
import base64
from services.database import fetch_data, save, DatabaseError
from services.auth import authenticate, roles, resolve_username
from services import sync
from views.employee import PAGES, render_employee
from views.work_tools import TOOLS, render_tool
from services.theme import apply_theme
from views.login import login_form
from views.workspace import sidebar_identity, sidebar_navigation, mobile_navigation, sync_status
from PIL import Image, ImageOps

st.set_page_config(page_title="HTCV | Quản lý nội bộ", layout="wide", initial_sidebar_state="auto")

FIREBASE_URL = "https://htcv-5c857-default-rtdb.firebaseio.com/htcv.json"

def update_firebase_user(path, data):
    return save(path, data)

def delete_firebase_user(path):
    return save(path, method='DELETE')

if not st.session_state.get('user'):
    apply_theme(st.session_state.get('theme') == 'Dark')

# ==========================================
# 1. HỆ THỐNG ĐĂNG NHẬP
# ==========================================
if "user" not in st.session_state or not st.session_state.user:
    with login_form():
        user_in = st.text_input("Tài khoản", placeholder="Nhập tên tài khoản", autocomplete="username").strip()
        pass_in = st.text_input("Mật khẩu", type="password", placeholder="Nhập mật khẩu", autocomplete="current-password")
        if st.form_submit_button("Đăng nhập", type="primary", use_container_width=True):
            if not user_in or not pass_in:
                st.error("Vui lòng nhập đầy đủ thông tin!")
            else:
                try:
                    db = fetch_data()
                except DatabaseError as exc:
                    st.error(str(exc))
                    st.stop()
                users = db.get("users", {})

                user_in = resolve_username(db, user_in)
                record = authenticate(db, user_in, pass_in)
                is_valid = record is not None

                if is_valid:
                    st.session_state.user = user_in
                    st.session_state.current_user = user_in
                    st.session_state.db = db

                    u_info = users.get(user_in, {})
                    st.session_state.current_shop = u_info.get("shop_id", "Shop Chính (Mặc định)")
                    role = str(u_info.get("role", "")).lower()

                    st.session_state.is_admin, st.session_state.is_super_admin = roles(user_in, u_info)

                    st.success("✅ Đăng nhập thành công!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Sai tài khoản hoặc mật khẩu. Liên hệ quản trị nếu cần đặt lại.")
    st.stop()

# ==========================================
# THIẾT LẬP THÔNG TIN KHI ĐÃ ĐĂNG NHẬP
# ==========================================
user_id = st.session_state.user
db = st.session_state.get("db", {})
u_info = db.get("users", {}).get(user_id, {})

if "show_bg" not in st.session_state: st.session_state.show_bg = False
if "show_pass" not in st.session_state: st.session_state.show_pass = False
if "theme" not in st.session_state: st.session_state.theme = "Light"
apply_theme(st.session_state.theme == 'Dark', u_info.get('bg_image', ''))

def close_settings_panels():
    st.session_state.show_bg = False
    st.session_state.show_pass = False
    for key in list(st.session_state):
        if str(key).startswith("editing_"):
            st.session_state[key] = False

# ==========================================
# 2. THANH MENU BÊN TRÁI (SIDEBAR) VỚI TÍNH NĂNG CHỌN NHÁNH
# ==========================================
with st.sidebar:
    sidebar_identity(user_id, st.session_state.get('is_admin'), st.session_state.get('is_super_admin'))
    st.caption("Web 2.7")

    # 🔓 MỞ KHÓA CHỌN CHI NHÁNH CHO ADMIN
    if st.session_state.get("is_super_admin", False):
        # Quét lấy toàn bộ danh sách các nhánh shop đang có trên Firebase
        db_shops = list(db.get("shops", {}).keys())
        all_shops = ["Shop Chính (Mặc định)"] + [s for s in db_shops if s != "Shop Chính (Mặc định)"]

        cur_shop = st.session_state.get("current_shop", "Shop Chính (Mặc định)")
        if cur_shop not in all_shops:
            all_shops.append(cur_shop)

        cur_idx = all_shops.index(cur_shop)

        # Bố trí Khung chọn (Dropdown)
        selected_shop = st.selectbox("Chi nhánh", all_shops, index=cur_idx)

        # Nếu Admin đổi nhánh -> Lưu vào RAM và Tải lại trang để load số liệu nhánh mới
        if selected_shop != cur_shop:
            st.session_state.current_shop = selected_shop
            st.rerun()
    else:
        # Nhân viên thường chỉ được xem (Khóa cứng nhánh)
        st.caption(st.session_state.get("current_shop", "Shop Chính (Mặc định)"))

    menu_options = [list(PAGES)[0]] + TOOLS + list(PAGES)[1:] + ['🤖 AI Tư Vấn']
    if st.session_state.get('is_admin') and st.session_state.get('navigation') == '👥 Quản Trị Admin':
        menu_options.append('👥 Quản Trị Admin')
    menu = sidebar_navigation(menu_options, TOOLS)
    edit_perms = u_info.get('edit_permissions', []) or []
    edit_permission = {'🛒 Lịch Ecom':'SỬA LỊCH ECOM','💰 Quỹ Shop':'QUẢN LÝ QUỸ SHOP',
                       '📍 Thị Trường':'SỬA THỊ TRƯỜNG','📈 Theo Dõi KPI':'SỬA SỐ KPI'}
    can_edit = menu in edit_permission and (st.session_state.get('is_admin') or edit_permission[menu] in edit_perms)
    edit_mode = False
    if can_edit:
        with st.expander('Chỉnh sửa dữ liệu', expanded=False):
            edit_mode = st.toggle('Mở phần chỉnh sửa', value=False, key='editing_'+menu)
            st.caption('Bật khi cần cập nhật. Chuyển chức năng sẽ trở về chế độ xem.')

    if st.session_state.get('is_admin'):
        def switch_admin():
            st.session_state.admin_task = 'Chọn tác vụ…'
            st.session_state.navigation = '🏠 Tổng quan' if st.session_state.get('navigation') == '👥 Quản Trị Admin' else '👥 Quản Trị Admin'
            close_settings_panels()
        st.button('Đóng công cụ quản trị' if menu == '👥 Quản Trị Admin' else 'Công cụ quản trị',
                  key='open_admin_tools', on_click=switch_admin, use_container_width=True)

    st.divider()
    if st.button("Làm mới dữ liệu", icon=":material/refresh:", use_container_width=True):
        sync.refresh(st.session_state, force=True)
        st.rerun()
    with st.expander('Tài khoản & giao diện', expanded=False):
        if st.button("Đổi hình nền", use_container_width=True):
            st.session_state.show_bg = not st.session_state.show_bg
            st.session_state.show_pass = False

        if st.button("Đổi mật khẩu", use_container_width=True):
            st.session_state.show_pass = not st.session_state.show_pass
            st.session_state.show_bg = False

        theme_label = "Giao diện Tối" if st.session_state.theme == "Light" else "Giao diện Sáng"
        if st.button(theme_label, use_container_width=True):
            st.session_state.theme = "Dark" if st.session_state.theme == "Light" else "Light"
            st.rerun()

        if st.button("Đăng xuất", use_container_width=True):
            st.session_state.clear()
            st.rerun()

# ==========================================
# 3. ĐIỀU HƯỚNG CHÍNH MÀN HÌNH
# ==========================================
mobile_navigation(menu_options)
if st.session_state.show_bg:
    st.info("Đổi hình nền cá nhân")
    bg_up = st.file_uploader("Chọn ảnh (Hệ thống tự nén cho nhẹ)", type=["png", "jpg", "jpeg"])
    c_bg1, c_bg2, c_bg3 = st.columns(3)

    if bg_up:
        if c_bg1.button("Áp dụng hình nền", type="primary", use_container_width=True):
            img = Image.open(bg_up)
            img = ImageOps.exif_transpose(img)
            img.thumbnail((1920, 1080))
            buffered = io.BytesIO()
            img.convert("RGB").save(buffered, format="JPEG", quality=85)
            img_str = base64.b64encode(buffered.getvalue()).decode()

            update_firebase_user(f"users/{user_id}/bg_image", img_str)
            st.session_state.db["users"][user_id]["bg_image"] = img_str
            st.session_state.show_bg = False
            st.success("Thành công!"); time.sleep(1); st.rerun()

    current_bg = u_info.get("bg_image", "")
    if current_bg:
        if c_bg2.button("Xóa hình nền", use_container_width=True):
            delete_firebase_user(f"users/{user_id}/bg_image")
            st.session_state.db["users"][user_id]["bg_image"] = ""
            st.session_state.show_bg = False
            st.success("Đã xóa nền!"); time.sleep(1); st.rerun()

    if c_bg3.button("Đóng cài đặt", use_container_width=True):
        st.session_state.show_bg = False
        st.rerun()

elif st.session_state.show_pass:
    st.info("Đổi mật khẩu")
    c_p1, c_p2 = st.columns(2)
    old_p = c_p1.text_input("Nhập mật khẩu cũ", type="password")
    new_p = c_p2.text_input("Nhập mật khẩu mới", type="password")

    c_btn1, c_btn2, c_btn3 = st.columns(3)
    if c_btn1.button("Lưu mật khẩu", type="primary", use_container_width=True):
        if not new_p.strip():
            st.error("Mật khẩu mới không được để trống.")
        elif old_p == str(u_info.get("pass", "")):
            update_firebase_user(f"users/{user_id}/pass", new_p)
            st.success("Đổi thành công! Đang đăng xuất...")
            time.sleep(1.5)
            st.session_state.clear()
            st.rerun()
        else:
            st.error("❌ Mật khẩu cũ sai!")

    if c_btn2.button("Đóng", use_container_width=True):
        st.session_state.show_pass = False
        st.rerun()

else:
    if menu in PAGES and not edit_mode:
        @st.fragment(run_every="30s")
        def employee_page():
            changed = st.session_state.get('_last_read_page') != menu
            sync.refresh(st.session_state, force=changed)
            if not st.session_state.get('user'):
                st.rerun()
            st.session_state['_last_read_page'] = menu
            if st.session_state.get('sync_error'):
                st.warning('Chưa tải được dữ liệu mới. Đang xem bản gần nhất đã tải thành công.')
            sync_status()
            render_employee(menu)
        employee_page()
    else:
        # Fresh role check before exposing any editable view.
        sync.refresh(st.session_state, force=True)
        if not st.session_state.get('user'): st.rerun()
        fresh_account=st.session_state.db.get('users',{}).get(st.session_state.user,{})
        if menu == '👥 Quản Trị Admin' and not st.session_state.get('is_admin'):
            st.warning('Tài khoản không có quyền quản trị.'); st.stop()
        if menu in edit_permission and not (st.session_state.get('is_admin') or edit_permission[menu] in (fresh_account.get('edit_permissions') or [])):
            st.warning('Tài khoản không có quyền chỉnh sửa.'); st.stop()
        if st.session_state.get('sync_error') and menu != '🤖 AI Tư Vấn':
            st.warning('Cần tải được dữ liệu mới trước khi chỉnh sửa.'); st.stop()
        if menu in TOOLS:
            render_tool(menu)
        elif menu == '🛒 Lịch Ecom':
            from views.ecom import render_ecom
            render_ecom()
        elif menu == '💰 Quỹ Shop':
            from views.fund import render_fund
            render_fund()
        elif menu == '📈 Theo Dõi KPI':
            from views.kpi import render_kpi
            render_kpi()
        elif menu == '📍 Thị Trường':
            from views.market import render_market
            render_market()
        elif menu == '🤖 AI Tư Vấn':
            from views.ai_chat import render_ai_chat
            render_ai_chat()
        elif menu == '👥 Quản Trị Admin':
            from views.admin import render_admin
            render_admin()
