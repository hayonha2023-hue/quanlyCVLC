import streamlit as st
import requests
import io
import base64
import hashlib
from PIL import Image, ImageOps

st.set_page_config(page_title="HTCV Web System", page_icon="🌐", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .html-card { background-color: #ffffff; padding: 25px; border-radius: 8px; border: 1px solid #e0e0e0; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); margin-bottom: 20px; }
    .html-title { color: #0D6EFD; font-family: Arial, sans-serif; font-weight: bold; text-align: center; margin-bottom: 5px; }
    .html-text { color: #6c757d; font-family: Arial, sans-serif; text-align: center; margin-top: 0px; }
    .stButton>button { border-radius: 5px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

FIREBASE_URL = "https://htcv-5c857-default-rtdb.firebaseio.com/htcv.json"
def update_firebase_user(path, data):
    requests.patch(f"https://htcv-5c857-default-rtdb.firebaseio.com/htcv/{path}.json", json=data)

def delete_firebase_user(path):
    requests.delete(f"https://htcv-5c857-default-rtdb.firebaseio.com/htcv/{path}.json")

def load_db():
    try:
        r = requests.get(FIREBASE_URL, timeout=10)
        if r.status_code == 200 and r.json():
            return r.json()
    except: pass
    return {}

# ÉP WEB LUÔN ĐỒNG BỘ REAL-TIME VỚI WINDOWS MỖI KHI THAO TÁC
st.session_state.db = load_db()

if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "current_shop" not in st.session_state:
    st.session_state.current_shop = "Shop Chính (Mặc định)"

def login_layout():
    st.markdown("<div class='html-card'><h2 class='html-title'>ĐĂNG NHẬP HỆ THỐNG</h2><p class='html-text'>HTCV Web Admin</p></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        user = st.text_input("👤 Tài khoản").strip().lower()
        pwd = st.text_input("🔑 Mật khẩu", type="password").strip()
        if st.button("ĐĂNG NHẬP", use_container_width=True, type="primary"):
            users = st.session_state.db.get("users", {})
            if (user == "admin" and pwd == "admin") or (user in users and users[user].get("pass") == pwd):
                st.session_state.current_user = user
                st.session_state.current_shop = users.get(user, {}).get("shop_id", "Shop Chính (Mặc định)") if user != "admin" else "Shop Chính (Mặc định)"
                st.rerun()
            else:
                st.error("Sai tài khoản hoặc mật khẩu!")

def main_layout():
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.current_user.upper()}")
        st.markdown(f"📍 **{st.session_state.current_shop}**")
        st.markdown("---")
        menu = st.radio("MAIN MENU", ["🛒 Lịch Ecom", "💰 Quỹ Shop", "📋 Xem Lịch", "📈 Theo Dõi KPI", "📊 Chia Target", "📍 Thị Trường", "🤖 AI Tư Vấn", "👥 Quản Trị Admin"])
      
        # --- CÁC NÚT CÀI ĐẶT CÁ NHÂN ---
        st.markdown("<br><hr style='border-color: rgba(150,150,150,0.1);'><br>", unsafe_allow_html=True)
        
        if st.button("🖼️ Đổi hình nền cá nhân", use_container_width=True):
            st.session_state.show_bg = not st.session_state.get("show_bg", False)
            st.session_state.show_pass = False

        if st.button("🔑 Cài đặt mật khẩu", use_container_width=True):
            st.session_state.show_pass = not st.session_state.get("show_pass", False)
            st.session_state.show_bg = False
            
        theme_txt = "☀️ Giao diện Sáng" if st.session_state.get("theme", "Dark") == "Dark" else "🌙 Giao diện Tối"
        if st.button(theme_txt, use_container_width=True):
            st.session_state.theme = "Light" if st.session_state.get("theme", "Dark") == "Dark" else "Dark"
            st.rerun()
            
        if st.button("🚪 Đăng xuất", use_container_width=True):
            st.session_state.clear()
            st.rerun()
        # --- FORM XỬ LÝ ẢNH & MẬT KHẨU ---
    user_id = st.session_state.get("user", "")
    
    if st.session_state.get("show_bg", False):
        st.info("🖼️ Đổi hình nền cá nhân")
        bg_up = st.file_uploader("Chọn ảnh từ máy (Hệ thống sẽ tự nén cho nhẹ)", type=["png", "jpg", "jpeg"])
        c_bg1, c_bg2 = st.columns(2)
        if bg_up:
            if c_bg1.button("💾 ÁP DỤNG MỚI", type="primary", use_container_width=True):
                img = Image.open(bg_up)
                img = ImageOps.exif_transpose(img)
                img.thumbnail((1920, 1080)) 
                buffered = io.BytesIO()
                img.convert("RGB").save(buffered, format="JPEG", quality=85)
                img_str = base64.b64encode(buffered.getvalue()).decode()
                update_firebase_user(f"users/{user_id}/bg_image", img_str)
                st.session_state.show_bg = False
                st.success("Thành công!"); time.sleep(1); st.rerun()
        
        current_bg = st.session_state.get("db", {}).get("users", {}).get(user_id, {}).get("bg_image", "")
        if current_bg:
            if c_bg2.button("🗑️ XÓA ẢNH NỀN", use_container_width=True):
                delete_firebase_user(f"users/{user_id}/bg_image")
                st.session_state.show_bg = False
                st.success("Đã xóa về mặc định!"); time.sleep(1); st.rerun()
        st.markdown("<hr>", unsafe_allow_html=True)

    if st.session_state.get("show_pass", False):
        st.info("🔑 Đổi Mật khẩu")
        c_p1, c_p2 = st.columns(2)
        old_p = c_p1.text_input("Mật khẩu cũ", type="password")
        new_p = c_p2.text_input("Mật khẩu mới", type="password")
        if st.button("💾 CẬP NHẬT MẬT KHẨU", type="primary"):
            real_old = st.session_state.get("db", {}).get("users", {}).get(user_id, {}).get("pass", "")
            if old_p == real_old:
                update_firebase_user(f"users/{user_id}/pass", new_p)
                st.success("Đổi thành công! Vui lòng đăng nhập lại."); time.sleep(1.5)
                st.session_state.clear(); st.rerun()
            else:
                st.error("❌ Sai mật khẩu cũ!")
        st.markdown("<hr>", unsafe_allow_html=True)

    if menu == "🛒 Lịch Ecom":
        from views.ecom import render_ecom
        render_ecom()
    elif menu == "💰 Quỹ Shop":
        from views.fund import render_fund
        render_fund()
    elif menu == "📋 Xem Lịch":
        from views.schedule import render_schedule
        render_schedule()
    elif menu == "📈 Theo Dõi KPI":
        from views.kpi import render_kpi
        render_kpi()
    elif menu == "📊 Chia Target":
        from views.target import render_target
        render_target()
    elif menu == "📍 Thị Trường":
        from views.market import render_market
        render_market()
    elif menu == "🤖 AI Tư Vấn":
        from views.ai_chat import render_ai_chat
        render_ai_chat()
    elif menu == "👥 Quản Trị Admin":
        from views.admin import render_admin
        render_admin()

if st.session_state.current_user is None:
    login_layout()
else:
    main_layout()
