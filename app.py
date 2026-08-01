import streamlit as st
import requests

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
        menu = st.radio("MAIN MENU", ["🛒 Lịch Ecom", "💰 Quỹ Shop", "📋 Xem Lịch", "📈 Theo Dõi KPI"])
        st.markdown("---")
        if st.button("👋 Đăng xuất", use_container_width=True):
            st.session_state.current_user = None
            st.rerun()

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

if st.session_state.current_user is None:
    login_layout()
else:
    main_layout()
