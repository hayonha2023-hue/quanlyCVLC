import streamlit as st
import requests
import time
import io
import base64
from services.database import fetch_data, save, DatabaseError
from services.auth import authenticate, roles
from services.theme import apply_theme
from PIL import Image, ImageOps

st.set_page_config(page_title="HTCV Web System", layout="wide", initial_sidebar_state="expanded")

FIREBASE_URL = "https://htcv-5c857-default-rtdb.firebaseio.com/htcv.json"

def update_firebase_user(path, data):
    return save(path, data)

def delete_firebase_user(path):
    return save(path, method='DELETE')

apply_theme(st.session_state.get('theme') == 'Dark')

# ==========================================
# 1. HỆ THỐNG ĐĂNG NHẬP
# ==========================================
if "user" not in st.session_state or not st.session_state.user:
    st.markdown("<h2 style='text-align: center; color: #0ea5e9; margin-top: 50px;'>HỆ THỐNG QUẢN TRỊ HTCV</h2>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2.form("login_form"):
        user_in = st.text_input("👤 Tài khoản").strip()
        pass_in = st.text_input("🔑 Mật khẩu", type="password")
        if st.form_submit_button("🚀 ĐĂNG NHẬP", use_container_width=True):
            if not user_in or not pass_in:
                st.error("Vui lòng nhập đầy đủ thông tin!")
            else:
                try:
                    db = fetch_data()
                except DatabaseError as exc:
                    st.error(str(exc))
                    st.stop()
                users = db.get("users", {})

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

def close_settings_panels():
    st.session_state.show_bg = False
    st.session_state.show_pass = False

# ==========================================
# 2. THANH MENU BÊN TRÁI (SIDEBAR) VỚI TÍNH NĂNG CHỌN NHÁNH
# ==========================================
with st.sidebar:
    st.markdown('<div class="htcv-brand">HTCV</div><div class="htcv-subtitle">Không gian quản lý công việc</div>', unsafe_allow_html=True)
    st.write("Tài khoản: " + str(user_id))
    st.caption("Web 2.1 • Dữ liệu dùng chung với HTCV")
    if st.button("↻ Làm mới dữ liệu", use_container_width=True):
        try:
            fresh = fetch_data()
        except DatabaseError as exc:
            st.error(str(exc))
            st.stop()
        if user_id not in fresh.get('users', {}):
            st.session_state.clear()
            st.rerun()
        st.session_state.db = fresh
        st.session_state.is_admin, st.session_state.is_super_admin = roles(user_id, fresh['users'][user_id])
        if not st.session_state.is_super_admin:
            st.session_state.current_shop = fresh['users'][user_id].get('shop_id', 'Shop Chính (Mặc định)')
        st.rerun()

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
        selected_shop = st.selectbox("📍 Chi Nhánh", all_shops, index=cur_idx)

        # Nếu Admin đổi nhánh -> Lưu vào RAM và Tải lại trang để load số liệu nhánh mới
        if selected_shop != cur_shop:
            st.session_state.current_shop = selected_shop
            st.rerun()
    else:
        # Nhân viên thường chỉ được xem (Khóa cứng nhánh)
        st.markdown(f"📍 {st.session_state.get('current_shop', 'Shop Chính (Mặc định)')}")

    st.markdown("<hr style='margin: 10px 0px;'>", unsafe_allow_html=True)

    menu_options = ["🛒 Lịch Ecom", "💰 Quỹ Shop", "📋 Xem Lịch", "📈 Theo Dõi KPI", "📊 Chia Target", "📍 Thị Trường", "🤖 AI Tư Vấn", "👥 Quản Trị Admin"]
    if not st.session_state.get('is_admin'):
        menu_options = [item for item in menu_options if item != "👥 Quản Trị Admin"]
    menu = st.radio("MAIN MENU", menu_options, label_visibility="collapsed", on_change=close_settings_panels)

    st.markdown("<br><hr style='border-color: rgba(150,150,150,0.1); margin: 10px 0px;'>", unsafe_allow_html=True)

    if st.button("🖼️ Đổi hình nền", use_container_width=True):
        st.session_state.show_bg = not st.session_state.show_bg
        st.session_state.show_pass = False

    if st.button("🔑 Đổi mật khẩu", use_container_width=True):
        st.session_state.show_pass = not st.session_state.show_pass
        st.session_state.show_bg = False

    theme_label = "🌙 Giao diện Tối" if st.session_state.theme == "Light" else "☀️ Giao diện Sáng"
    if st.button(theme_label, use_container_width=True):
        st.session_state.theme = "Dark" if st.session_state.theme == "Light" else "Light"
        st.rerun()

    if st.button("🚪 Đăng xuất", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# ==========================================
# 3. ĐIỀU HƯỚNG CHÍNH MÀN HÌNH
# ==========================================
if st.session_state.show_bg:
    st.info("🖼️ ĐỔI HÌNH NỀN CÁ NHÂN (Tự động áp dụng sau khi tải xong)")
    bg_up = st.file_uploader("Chọn ảnh (Hệ thống tự nén cho nhẹ)", type=["png", "jpg", "jpeg"])
    c_bg1, c_bg2, c_bg3 = st.columns(3)

    if bg_up:
        if c_bg1.button("💾 ÁP DỤNG", type="primary", use_container_width=True):
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
        if c_bg2.button("🗑️ XÓA NỀN", use_container_width=True):
            delete_firebase_user(f"users/{user_id}/bg_image")
            st.session_state.db["users"][user_id]["bg_image"] = ""
            st.session_state.show_bg = False
            st.success("Đã xóa nền!"); time.sleep(1); st.rerun()

    if c_bg3.button("❌ ĐÓNG CÀI ĐẶT", use_container_width=True):
        st.session_state.show_bg = False
        st.rerun()

elif st.session_state.show_pass:
    st.info("🔑 THAY ĐỔI MẬT KHẨU")
    c_p1, c_p2 = st.columns(2)
    old_p = c_p1.text_input("Nhập mật khẩu cũ", type="password")
    new_p = c_p2.text_input("Nhập mật khẩu mới", type="password")

    c_btn1, c_btn2, c_btn3 = st.columns(3)
    if c_btn1.button("💾 CẬP NHẬT", type="primary", use_container_width=True):
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

    if c_btn2.button("❌ ĐÓNG", use_container_width=True):
        st.session_state.show_pass = False
        st.rerun()

else:
    if menu == "🛒 Lịch Ecom":
        try: from views.ecom import render_ecom; render_ecom()
        except Exception as e: st.warning(f"Tính năng đang bảo trì: {e}")
    elif menu == "💰 Quỹ Shop":
        try: from views.fund import render_fund; render_fund()
        except Exception as e: st.warning(f"Tính năng đang bảo trì: {e}")
    elif menu == "📋 Xem Lịch":
        try: from views.schedule import render_schedule; render_schedule()
        except Exception as e: st.warning(f"Tính năng đang bảo trì: {e}")
    elif menu == "📈 Theo Dõi KPI":
        try: from views.kpi import render_kpi; render_kpi()
        except Exception as e: st.warning(f"Tính năng đang bảo trì: {e}")
    elif menu == "📊 Chia Target":
        try: from views.target import render_target; render_target()
        except Exception as e: st.warning(f"Tính năng đang bảo trì: {e}")
    elif menu == "📍 Thị Trường":
        try: from views.market import render_market; render_market()
        except Exception as e: st.warning(f"Tính năng đang bảo trì: {e}")
    elif menu == "🤖 AI Tư Vấn":
        try: from views.ai_chat import render_ai_chat; render_ai_chat()
        except Exception as e: st.warning(f"Tính năng đang bảo trì: {e}")
    elif menu == "👥 Quản Trị Admin":
        try: from views.admin import render_admin; render_admin()
        except Exception as e: st.warning(f"Tính năng đang bảo trì: {e}")

apply_theme(st.session_state.theme == 'Dark', u_info.get('bg_image', ''))
