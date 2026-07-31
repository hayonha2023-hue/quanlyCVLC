import streamlit as st

# Cấu hình trang Web
st.set_page_config(page_title="HTCV Web System", page_icon="🌐", layout="wide", initial_sidebar_state="expanded")

# NHÚNG MÃ HTML/CSS ĐỂ GIAO DIỆN ĐẸP NHƯ WEB THẬT
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

# Bộ nhớ tạm
if "current_user" not in st.session_state:
    st.session_state.current_user = None

def login_layout():
    st.markdown("""
    <div class='html-card'>
        <h2 class='html-title'>ĐĂNG NHẬP HỆ THỐNG</h2>
        <p class='html-text'>HTCV Web Admin</p>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        user = st.text_input("👤 Tài khoản")
        pwd = st.text_input("🔑 Mật khẩu", type="password")
        if st.button("ĐĂNG NHẬP", use_container_width=True, type="primary"):
            if user == "admin" and pwd == "admin":
                st.session_state.current_user = "admin"
                st.rerun()
            else:
                st.error("Sai tài khoản hoặc mật khẩu!")

def main_layout():
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.current_user.upper()}")
        st.markdown("📍 **Shop Chính (Mặc định)**")
        st.markdown("---")
        menu = st.radio("MAIN MENU", ["🛒 Lịch Ecom", "💰 Quỹ Shop", "📋 Xem Lịch"])
        st.markdown("---")
        if st.button("👋 Đăng xuất", use_container_width=True):
            st.session_state.current_user = None
            st.rerun()

    # Điều hướng sang các file chức năng
    if menu == "🛒 Lịch Ecom":
        from views.ecom import render_ecom
        render_ecom()
    elif menu == "💰 Quỹ Shop":
        st.markdown("<div class='html-card'><h3 class='html-title' style='text-align: left;'>💰 SỔ QUỸ SHOP</h3></div>", unsafe_allow_html=True)
    elif menu == "📋 Xem Lịch":
        st.markdown("<div class='html-card'><h3 class='html-title' style='text-align: left;'>📋 LỊCH TRỰC TUẦN</h3></div>", unsafe_allow_html=True)

if st.session_state.current_user is None:
    login_layout()
else:
    main_layout()
