import streamlit as st
import requests

# 1. Cấu hình trang Web
st.set_page_config(page_title="HTCV Web System", page_icon="🌐", layout="wide", initial_sidebar_state="expanded")

# 2. Giao diện CSS
st.markdown("""
<style>
    .html-card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .html-title { color: #0D6EFD; font-family: Arial, sans-serif; font-weight: bold; text-align: center; margin-bottom: 5px; }
    .html-text { color: #6c757d; font-family: Arial, sans-serif; text-align: center; margin-top: 0px; }
    .stButton>button { border-radius: 5px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 3. KẾT NỐI CƠ SỞ DỮ LIỆU ĐÁM MÂY (FIREBASE)
FIREBASE_URL = "https://htcv-5c857-default-rtdb.firebaseio.com/htcv.json"

def load_db():
    try:
        r = requests.get(FIREBASE_URL, timeout=10)
        if r.status_code == 200 and r.json():
            return r.json()
    except: pass
    return {}

# 4. Khởi tạo bộ nhớ tạm (Session State)
if "db" not in st.session_state:
    st.session_state.db = load_db()
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "current_shop" not in st.session_state:
    st.session_state.current_shop = "Shop Chính (Mặc định)"

# 5. Giao diện Đăng nhập
def login_layout():
    st.markdown("""
    <div class='html-card'>
        <h2 class='html-title'>ĐĂNG NHẬP HỆ THỐNG</h2>
        <p class='html-text'>HTCV Web Admin</p>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        user = st.text_input("👤 Tài khoản").strip().lower()
        pwd = st.text_input("🔑 Mật khẩu", type="password").strip()
        if st.button("ĐĂNG NHẬP", use_container_width=True, type="primary"):
            # Quét mật khẩu từ Firebase
            users = st.session_state.db.get("users", {})
            if (user == "admin" and pwd == "admin") or (user in users and users[user].get("pass") == pwd):
                st.session_state.current_user = user
                st.session_state.current_shop = users.get(user, {}).get("shop_id", "Shop Chính (Mặc định)") if user != "admin" else "Shop Chính (Mặc định)"
                st.rerun()
            else:
                st.error("Sai tài khoản hoặc mật khẩu!")

# 6. Giao diện Bảng điều khiển (Menu)
def main_layout():
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.current_user.upper()}")
        st.markdown(f"📍 **{st.session_state.current_shop}**")
        st.markdown("---")
        menu = st.radio("MAIN MENU", ["🛒 Lịch Ecom", "💰 Quỹ Shop", "📋 Xem Lịch"])
        st.markdown("---")
        if st.button("🔄 Tải lại dữ liệu"):
            st.session_state.db = load_db()
            st.rerun()
        if st.button("👋 Đăng xuất", use_container_width=True):
            st.session_state.current_user = None
            st.rerun()

    # Điều hướng sang các file chức năng
    if menu == "🛒 Lịch Ecom":
        from views.ecom import render_ecom
        render_ecom()
    elif menu == "💰 Quỹ Shop":
        from views.fund import render_fund
        render_fund()
    elif menu == "📋 Xem Lịch":
        st.markdown("<div class='html-card'><h3 class='html-title' style='text-align: left;'>📋 LỊCH TRỰC TUẦN</h3><p class='html-text' style='text-align: left;'>Lịch trực đã được hệ thống phân bổ.</p></div>", unsafe_allow_html=True)

# 7. Trục chạy chính
if st.session_state.current_user is None:
    login_layout()
else:
    main_layout()
