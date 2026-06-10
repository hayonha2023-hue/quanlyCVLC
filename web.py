import streamlit as st
import requests

st.set_page_config(page_title="HTCV Mobile", layout="wide")

# Code tàng hình giao diện thừa
hide_st_style = """<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;} [data-testid="stToolbar"] {visibility: hidden !important;}</style>"""
st.markdown(hide_st_style, unsafe_allow_html=True)

FIREBASE_URL = "https://htcv-5c857-default-rtdb.firebaseio.com/htcv.json"

def get_data():
    try:
        r = requests.get(FIREBASE_URL)
        return r.json() if r.status_code == 200 else {}
    except: return {}

db = get_data()

if "user" not in st.session_state: st.session_state.user = None

if st.session_state.user is None:
    # --- ĐĂNG NHẬP ---
    st.title("📱 HTCV MOBILE")
    u = st.text_input("Tài khoản").strip().lower()
    p = st.text_input("Mật khẩu", type="password")
    if st.button("ĐĂNG NHẬP"):
        users = db.get("users", {})
        if u in users and users[u]["pass"] == p:
            st.session_state.user = u
            st.rerun()
        else: st.error("Sai thông tin!")
else:
    # --- PHÂN QUYỀN VÀ HIỂN THỊ ---
    u_info = db.get("users", {}).get(st.session_state.user, {})
    is_admin = u_info.get("role") == "admin"
    perms = u_info.get("permissions", [])
    
    with st.sidebar:
        st.write(f"👤 Xin chào, {st.session_state.user}")
        if st.button("Đăng xuất"): st.session_state.user = None; st.rerun()

    # Danh sách chức năng đầy đủ
    all_tabs = ["🎯 KPI", "🗓️ LỊCH", "💰 QUỸ SHOP", "📦 LẬP HÀNG", "📞 DANH BẠ"]
    
    # Lọc tab dựa trên quyền
    allowed_tabs = []
    if is_admin: allowed_tabs = all_tabs
    else:
        if "XEM LỊCH" in perms: allowed_tabs.append("🗓️ LỊCH")
        if "TÍCH LŨY" in perms: allowed_tabs.append("🎯 KPI")
        if "QUỸ SHOP" in perms: allowed_tabs.append("💰 QUỸ SHOP")
        # ... thêm các quyền khác ở đây nếu cần

    if not allowed_tabs:
        st.warning("Tài khoản chưa được cấp quyền truy cập tính năng nào!")
    else:
        tabs = st.tabs(allowed_tabs)
        for i, tab_name in enumerate(allowed_tabs):
            with tabs[i]:
                if tab_name == "🎯 KPI":
                    st.subheader("Bảng KPI")
                    # Hiển thị dữ liệu KPI từ db
                elif tab_name == "🗓️ LỊCH":
                    st.subheader("Lịch trực")
                    # Hiển thị dữ liệu lịch
                elif tab_name == "💰 QUỸ SHOP":
                    st.subheader("Quỹ Shop")
                    # Hiển thị dữ liệu Quỹ
                elif tab_name == "📦 LẬP HÀNG":
                    st.subheader("Đối chiếu hàng hóa")
                elif tab_name == "📞 DANH BẠ":
                    st.subheader("Danh bạ nhân viên")
