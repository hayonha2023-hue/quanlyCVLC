import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime, timedelta

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

def delete_firebase(path):
    url = f"https://htcv-5c857-default-rtdb.firebaseio.com/{path}.json"
    requests.delete(url)

# Hàm định dạng tiền tệ VNĐ (vd: 1.500.000)
def format_vnd(amount):
    return f"{amount:,.0f}".replace(",", ".")

# --- KHỞI TẠO SESSION ---
if "user" not in st.session_state:
    st.session_state.user = None
    st.session_state.is_admin = False

db = get_data()

# ==========================================
# MÀN HÌNH ĐĂNG NHẬP
# ==========================================
if st.session_state.user is None:
    st.markdown("<h2 style='text-align: center; color: #0ea5e9;'>📱 HTCV MOBILE</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Đăng nhập để vào hệ thống</p>", unsafe_allow_html=True)
    
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

    # TẠO 3 TAB CHỨC NĂNG ĐỂ VUỐT TRÊN ĐIỆN THOẠI
    tab1, tab2, tab3 = st.tabs(["🎯 KPI", "🗓️ LỊCH", "💰 QUỸ SHOP"])

    # --- TAB 1: BẢNG TIẾN ĐỘ KPI ---
    with tab1:
        st.markdown("<h3 style='color: #0ea5e9;'>Tiến Độ KPI Tháng Này</h3>", unsafe_allow_html=True)
        kpi_data = db.get("kpi", {}).get("emp", {})
        
        if not kpi_data:
            st.info("Chưa có dữ liệu KPI tháng này.")
        else:
            tot_t = sum(d.get("tgt", 0) for d in kpi_data.values())
            tot_s = sum(d.get("sold", 0) for d in kpi_data.values())
            pct = (tot_s / tot_t * 100) if tot_t > 0 else 0
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Tổng Target", f"{tot_t}")
            col2.metric("Đã bán", f"{tot_s}")
            col3.metric("Tiến độ", f"{pct:.1f}%")
            
            st.divider()

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
                    
                    with c2:
                        if st.session_state.is_admin:
                            new_sold = st.number_input("Cập nhật", value=sold, step=1, key=f"upd_{emp_name}", label_visibility="collapsed")
                            if new_sold != sold:
                                update_firebase(f"kpi/emp/{emp_name}", {"sold": new_sold})
                                st.rerun()
                        else:
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

    # --- TAB 3: QUẢN LÝ QUỸ SHOP ---
    with tab3:
        st.markdown("<h3 style='color: #0ea5e9;'>Quản Lý Sổ Quỹ</h3>", unsafe_allow_html=True)
        
        quy_shop = db.get("quy_shop", {})
        
        # Tính toán Dòng tiền
        tong_thu = sum(item.get("amount", 0) for item in quy_shop.values() if item.get("type") == "Thu")
        tong_chi = sum(item.get("amount", 0) for item in quy_shop.values() if item.get("type") == "Chi")
        ton_quy = tong_thu - tong_chi
        
        # Bảng Tổng Quan
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 TỒN QUỸ", f"{format_vnd(ton_quy)} đ")
        c2.metric("📈 Tổng Thu", f"{format_vnd(tong_thu)} đ")
        c3.metric("📉 Tổng Chi", f"{format_vnd(tong_chi)} đ")
        
        st.divider()
        
        # Chỉ Admin mới thấy Khung Nhập Liệu
        if st.session_state.is_admin:
            with st.expander("➕ THÊM KHOẢN THU / CHI MỚI", expanded=False):
                with st.form("form_quy", clear_on_submit=True):
                    f_type = st.selectbox("Loại Giao Dịch", ["Thu", "Chi"])
                    f_amount = st.number_input("Số tiền (VNĐ)", min_value=0, step=50000)
                    f_desc = st.text_input("Chi tiết / Lý do (Vd: Bán hàng, Tiền điện...)")
                    
                    if st.form_submit_button("LƯU VÀO SỔ", use_container_width=True):
                        if f_amount > 0 and f_desc.strip():
                            # Sinh mã ID ngẫu nhiên theo thời gian thực
                            record_id = str(int(time.time() * 1000))
                            # Lấy giờ Việt Nam (UTC+7)
                            now_str = (datetime.utcnow() + timedelta(hours=7)).strftime("%d/%m/%Y %H:%M")
                            new_record = {
                                "date": now_str,
                                "type": f_type,
                                "amount": f_amount,
                                "desc": f_desc.strip(),
                                "user": st.session_state.user
                            }
                            update_firebase("quy_shop", {record_id: new_record})
                            st.success("✅ Đã lưu vào sổ quỹ!")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("❌ Vui lòng nhập số tiền và chi tiết!")
        else:
            st.info("💡 Chỉ Admin mới có quyền thêm hoặc xóa khoản thu/chi.")

        st.markdown("#### 📜 Lịch Sử Giao Dịch")
        if not quy_shop:
            st.caption("Sổ quỹ đang trống.")
        else:
            # Sắp xếp mới nhất lên đầu
            sorted_records = sorted(quy_shop.items(), key=lambda x: x[0], reverse=True)
            
            for rec_id, rec in sorted_records:
                with st.container():
                    col_text, col_btn = st.columns([5, 1])
                    
                    color = "#10b981" if rec["type"] == "Thu" else "#ef4444"
                    icon = "➕" if rec["type"] == "Thu" else "➖"
                    
                    with col_text:
                        st.markdown(f"""
                        <div style='line-height: 1.4;'>
                            <strong>{rec.get('date', '')}</strong> <span style='color: gray; font-size: 0.85em;'>(nhập bởi {rec.get('user', 'admin')})</span><br>
                            <span style='color: {color}; font-weight: bold; font-size: 1.1em;'>{icon} {format_vnd(rec.get('amount', 0))} đ</span><br>
                            📝 {rec.get('desc', '')}
                        </div>
                        """, unsafe_allow_html=True)
                        
                    with col_btn:
                        # Chỉ Admin mới có nút Xóa
                        if st.session_state.is_admin:
                            if st.button("❌", key=f"del_{rec_id}", help="Xóa giao dịch này"):
                                delete_firebase(f"quy_shop/{rec_id}")
                                st.rerun()
                st.markdown("---")
