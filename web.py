import streamlit as st
import requests
import pandas as pd

# Cấu hình giao diện chuẩn Mobile
st.set_page_config(page_title="HTCV Mobile", page_icon="📱", layout="wide")

FIREBASE_URL = "https://htcv-5c857-default-rtdb.firebaseio.com/htcv.json"

# --- CÁC HÀM XỬ LÝ DỮ LIỆU ---
def get_data():
    try:
        r = requests.get(FIREBASE_URL)
        if r.status_code == 200 and r.json() is not None:
            return r.json()
    except:
        pass
    return {}

def update_firebase(path, data):
    url = f"https://htcv-5c857-default-rtdb.firebaseio.com/{path}.json"
    requests.patch(url, json=data)

# --- KHỞI TẠO SESSION (LƯU TRẠNG THÁI ĐĂNG NHẬP) ---
if "user" not in st.session_state:
    st.session_state.user = None
    st.session_state.is_admin = False

db = get_data()

# ==========================================
# MÀN HÌNH ĐĂNG NHẬP
# ==========================================
if st.session_state.user is None:
    st.markdown("<h2 style='text-align: center; color: #0ea5e9;'>📱 HTCV MOBILE</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Đăng nhập để xem Lịch & KPI</p>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Tài khoản")
        password = st.text_input("Mật khẩu", type="password")
        submitted = st.form_submit_button("ĐĂNG NHẬP", use_container_width=True)
        
        if submitted:
            users = db.get("users", {})
            u_lower = username.strip().lower()
            if u_lower in users and users[u_lower]["pass"] == password:
                st.session_state.user = u_lower
                st.session_state.is_admin = (users[u_lower].get("role") == "admin")
                st.rerun()
            else:
                st.error("❌ Sai tài khoản hoặc mật khẩu!")

# ==========================================
# MÀN HÌNH CHÍNH (SAU KHI ĐĂNG NHẬP)
# ==========================================
else:
    # THANH MENU BÊN TRÁI
    with st.sidebar:
        role_text = "Admin" if st.session_state.is_admin else "Nhân viên"
        st.markdown(f"### 👤 {st.session_state.user.upper()} ({role_text})")
        if st.button("🚪 Đăng xuất", use_container_width=True):
            st.session_state.user = None
            st.session_state.is_admin = False
            st.rerun()

    # TẠO 2 TAB ĐỂ VUỐT TRÊN ĐIỆN THOẠI
    tab1, tab2 = st.tabs(["🎯 BẢNG KPI", "🗓️ LỊCH TRỰC"])

    # --- TAB 1: BẢNG TIẾN ĐỘ KPI ---
    with tab1:
        st.markdown("<h3 style='color: #0ea5e9;'>Tiến Độ KPI Tháng Này</h3>", unsafe_allow_html=True)
        kpi_data = db.get("kpi", {}).get("emp", {})
        
        if not kpi_data:
            st.info("Chưa có dữ liệu KPI tháng này.")
        else:
            # Hiện tổng quan
            tot_t = sum(d.get("tgt", 0) for d in kpi_data.values())
            tot_s = sum(d.get("sold", 0) for d in kpi_data.values())
            pct = (tot_s / tot_t * 100) if tot_t > 0 else 0
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Tổng Target", f"{tot_t}")
            col2.metric("Đã bán", f"{tot_s}")
            col3.metric("Tiến độ", f"{pct:.1f}%")
            
            st.divider()

            # Hiển thị từng người (Dạng thẻ cho điện thoại dễ nhìn)
            for emp_name, emp_info in kpi_data.items():
                tgt = emp_info.get("tgt", 0)
                sold = emp_info.get("sold", 0)
                rem = tgt - sold
                
                with st.container():
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"**{emp_name}**")
                        st.progress(sold / tgt if tgt > 0 and sold <= tgt else (1.0 if sold > tgt else 0.0))
                        st.caption(f"Đã bán: **{sold}** / Target: **{tgt}** (Còn: {rem if rem>0 else 0})")
                    
                    # NẾU LÀ ADMIN -> CHO PHÉP NHẬP SỐ BÁN NGAY TRÊN ĐIỆN THOẠI
                    with c2:
                        if st.session_state.is_admin:
                            new_sold = st.number_input("Cập nhật", value=sold, step=1, key=f"upd_{emp_name}", label_visibility="collapsed")
                            if new_sold != sold:
                                # Gửi thẳng lệnh cập nhật lên Cloud
                                update_firebase(f"kpi/emp/{emp_name}", {"sold": new_sold})
                                st.rerun()
                        else:
                            # NẾU LÀ NHÂN VIÊN -> CHỈ HIỆN TRẠNG THÁI
                            if rem <= 0:
                                st.success("Xong!")
                            else:
                                st.warning(f"Thiếu {rem}")
                st.markdown("---")

    # --- TAB 2: LỊCH TRỰC ---
    with tab2:
        st.markdown("<h3 style='color: #0ea5e9;'>Lịch Trực Gần Nhất</h3>", unsafe_allow_html=True)
        history = db.get("detailed_history", {})
        
        if not history:
            st.info("Chưa có lịch trực.")
        else:
            for date_str, shifts in history.items():
                with st.expander(f"📅 {date_str}", expanded=True):
                    sang = ", ".join(shifts.get("Sáng", [])) if shifts.get("Sáng") else "Trống"
                    chieu = ", ".join(shifts.get("Chiều", [])) if shifts.get("Chiều") else "Trống"
                    toi = ", ".join(shifts.get("10h30", [])) if shifts.get("10h30") else "Trống"
                    
                    st.markdown(f"**☀️ Sáng:** {sang}")
                    st.markdown(f"**🌤️ Chiều:** {chieu}")
                    st.markdown(f"**🌙 10h30:** {toi}")