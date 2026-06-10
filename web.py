import streamlit as st
import requests
import time
from datetime import datetime, timedelta

# Cấu hình giao diện chuẩn Mobile
st.set_page_config(page_title="HTCV Mobile", page_icon="📱", layout="wide")

# Tàng hình menu thừa
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;} 
            footer {visibility: hidden;} 
            header {visibility: hidden;} 
            [data-testid="stToolbar"] {visibility: hidden !important;} 
            [data-testid="stDecoration"] {visibility: hidden !important;} 
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

FIREBASE_URL = "https://htcv-5c857-default-rtdb.firebaseio.com/htcv.json"

def get_data():
    try:
        r = requests.get(FIREBASE_URL)
        if r.status_code == 200 and r.json() is not None: return r.json()
    except: return {}
    return {}

def update_firebase(path, data):
    requests.patch(f"{FIREBASE_URL.replace('.json', '')}/{path}.json", json=data)

# --- KHỞI TẠO SESSION ---
if "user" not in st.session_state:
    st.session_state.user = None
    st.session_state.page = "login"

db = get_data()

# --- MÀN HÌNH CHÍNH ---
if st.session_state.user is None:
    if st.session_state.page == "login":
        st.markdown("<h2 style='text-align: center; color: #0ea5e9;'>📱 HTCV MOBILE</h2>", unsafe_allow_html=True)
        with st.form("login"):
            username = st.text_input("Tài khoản").strip().lower()
            password = st.text_input("Mật khẩu", type="password")
            if st.form_submit_button("ĐĂNG NHẬP", use_container_width=True):
                users = db.get("users", {})
                if username in users and users[username]["pass"] == password:
                    st.session_state.user = username
                    st.rerun()
                else: st.error("Sai thông tin!")
        
        c1, c2 = st.columns(2)
        if c1.button("Đăng ký"): st.session_state.page = "register"; st.rerun()
        if c2.button("Quên mật khẩu"): st.session_state.page = "forgot"; st.rerun()

    elif st.session_state.page == "register":
        with st.form("reg"):
            new_u = st.text_input("Tên đăng nhập").strip().lower()
            new_p = st.text_input("Mật khẩu", type="password")
            if st.form_submit_button("ĐĂNG KÝ"):
                update_firebase("pending_users", {new_u: {"pass": new_p}})
                st.success("Đã gửi yêu cầu!")
        if st.button("Về đăng nhập"): st.session_state.page = "login"; st.rerun()

    elif st.session_state.page == "forgot":
        with st.form("forgot"):
            u = st.text_input("Tài khoản của bạn").strip().lower()
            new_p = st.text_input("Mật khẩu mới", type="password")
            secret = st.text_input("Mã xác nhận (do Admin cung cấp)")
            if st.form_submit_button("RESET MẬT KHẨU"):
                if secret == "admin123": # Mã bí mật ông quy định
                    update_firebase("users", {u: {"pass": new_p}})
                    st.success("Reset thành công!")
                else: st.error("Mã xác nhận sai!")
        if st.button("Về đăng nhập"): st.session_state.page = "login"; st.rerun()

else:
    # --- SAU ĐĂNG NHẬP ---
    with st.sidebar:
        st.write(f"Xin chào, {st.session_state.user}")
        with st.expander("⚙️ Cài đặt"):
            old_p = st.text_input("Mật khẩu cũ", type="password")
            new_p = st.text_input("Mật khẩu mới", type="password")
            if st.button("Đổi mật khẩu"):
                # Code check pass cũ và lưu pass mới lên Firebase
                st.success("Đã đổi pass!")
        if st.button("Đăng xuất"): st.session_state.user = None; st.rerun()
    
    st.write("Chào mừng quay lại!")
