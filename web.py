import streamlit as st
import requests
import time
from datetime import datetime, timedelta

# ==========================================
# CẤU HÌNH GIAO DIỆN & TÀNG HÌNH NÚT THỪA
# ==========================================
st.set_page_config(page_title="HTCV System", page_icon="⚡", layout="wide")

# CSS GIẤU MANAGE APP VÀ LÀM ĐẸP GIAO DIỆN
custom_css = """
<style>
    /* Giấu toàn bộ Menu, Header, Footer của Streamlit */
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;} 
    header {visibility: hidden;} 
    [data-testid="stToolbar"] {visibility: hidden !important;} 
    [data-testid="stDecoration"] {visibility: hidden !important;} 
    
    /* TIÊU DIỆT NÚT MANAGE APP MÀU ĐEN Ở GÓC DƯỚI CÙNG */
    .viewerBadge_container {display: none !important;}
    #viewerBadge_container_0 {display: none !important;}
    .viewerBadge_link {display: none !important;}
    
    /* Làm mượt nút bấm */
    .stButton>button {
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# CƠ SỞ DỮ LIỆU FIREBASE
# ==========================================
FIREBASE_URL = "https://htcv-5c857-default-rtdb.firebaseio.com/htcv.json"

def get_data():
    try:
        r = requests.get(FIREBASE_URL)
        return r.json() if r.status_code == 200 else {}
    except: return {}

def update_firebase(path, data):
    requests.patch(f"{FIREBASE_URL.replace('.json', '')}/{path}.json", json=data)

def delete_firebase(path):
    requests.delete(f"{FIREBASE_URL.replace('.json', '')}/{path}.json")

def format_vnd(amount):
    return f"{amount:,.0f} ₫".replace(",", ".")

# ==========================================
# KHỞI TẠO BIẾN TRẠNG THÁI (SESSION)
# ==========================================
if "user" not in st.session_state:
    st.session_state.user = None
    st.session_state.is_admin = False
    st.session_state.page = "login"
if "theme" not in st.session_state:
    st.session_state.theme = "Dark" # Mặc định giao diện tối sang trọng

db = get_data()

# --- Áp dụng Theme Sáng/Tối ---
if st.session_state.theme == "Light":
    st.markdown("""<style>.stApp {background-color: #f8fafc; color: #0f172a;} .stMarkdown, .stText {color: #0f172a !important;}</style>""", unsafe_allow_html=True)

# ==========================================
# MÀN HÌNH ĐĂNG NHẬP / ĐĂNG KÝ
# ==========================================
if st.session_state.user is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #0ea5e9;'>⚡ HTCV SYSTEM</h1>", unsafe_allow_html=True)
    
    if st.session_state.page == "login":
        st.markdown("<p style='text-align: center; color: gray;'>Đăng nhập để vào hệ thống</p>", unsafe_allow_html=True)
        with st.form("login_form"):
            u = st.text_input("👤 Tài khoản").strip().lower()
            p = st.text_input("🔑 Mật khẩu", type="password")
            if st.form_submit_button("🚀 ĐĂNG NHẬP", use_container_width=True):
                users = db.get("users", {})
                if u in users and users[u]["pass"] == p:
                    st.session_state.user = u
                    st.session_state.is_admin = (users[u].get("role") == "admin")
                    st.rerun()
                elif u in db.get("pending_users", {}): st.warning("⏳ Tài khoản đang chờ Admin duyệt!")
                else: st.error("❌ Sai thông tin đăng nhập!")
                
        col1, col2 = st.columns(2)
        if col1.button("📝 Đăng ký mới", use_container_width=True): st.session_state.page = "register"; st.rerun()
        if col2.button("❓ Quên mật khẩu", use_container_width=True): st.session_state.page = "forgot"; st.rerun()

    elif st.session_state.page == "register":
        st.markdown("<h4 style='text-align: center;'>ĐĂNG KÝ TÀI KHOẢN</h4>", unsafe_allow_html=True)
        with st.form("reg_form"):
            new_u = st.text_input("Tên đăng nhập (Viết liền không dấu)").strip().lower()
            new_p = st.text_input("Mật khẩu", type="password")
            if st.form_submit_button("GỬI YÊU CẦU", use_container_width=True):
                if new_u and new_p:
                    update_firebase("pending_users", {new_u: {"pass": new_p}})
                    st.success("✅ Đã gửi! Vui lòng báo Admin duyệt.")
                else: st.error("Nhập đủ thông tin!")
        if st.button("⬅ Quay lại", use_container_width=True): st.session_state.page = "login"; st.rerun()

    elif st.session_state.page == "forgot":
        st.markdown("<h4 style='text-align: center;'>KHÔI PHỤC MẬT KHẨU</h4>", unsafe_allow_html=True)
        with st.form("forgot_form"):
            u = st.text_input("Tài khoản của bạn").strip().lower()
            new_p = st.text_input("Mật khẩu mới", type="password")
            secret = st.text_input("Mã bảo mật (Hỏi Admin)")
            if st.form_submit_button("ĐỔI MẬT KHẨU", use_container_width=True):
                if secret == "admin123":
                    update_firebase("users", {u: {"pass": new_p}})
                    st.success("✅ Đổi thành công! Vui lòng đăng nhập lại.")
                else: st.error("❌ Mã bảo mật sai!")
        if st.button("⬅ Quay lại", use_container_width=True): st.session_state.page = "login"; st.rerun()

# ==========================================
# MÀN HÌNH CHÍNH (SAU KHI ĐĂNG NHẬP)
# ==========================================
else:
    u_info = db.get("users", {}).get(st.session_state.user, {})
    perms = u_info.get("permissions", [])
    
    # --- THANH BÊN (SIDEBAR) CHUYÊN NGHIỆP ---
    with st.sidebar:
        st.markdown(f"<h2 style='color:#0ea5e9; text-align:center;'>HTCV</h2>", unsafe_allow_html=True)
        st.divider()
        
        # HIỂN THỊ RÕ RÀNG QUYỀN ADMIN HAY NHÂN VIÊN
        if st.session_state.is_admin:
            st.success("👑 QUYỀN ADMIN")
            st.markdown(f"**Xin chào, {st.session_state.user.upper()}**")
        else:
            st.info("👤 QUYỀN NHÂN VIÊN")
            st.markdown(f"**Xin chào, {st.session_state.user.upper()}**")
            
        st.divider()
        
        # NÚT ĐỔI MÀU SÁNG / TỐI
        theme_icon = "🌞 Giao diện Sáng" if st.session_state.theme == "Dark" else "🌙 Giao diện Tối"
        if st.button(theme_icon, use_container_width=True):
            st.session_state.theme = "Light" if st.session_state.theme == "Dark" else "Dark"
            st.rerun()
            
        # NÚT ĐỔI MẬT KHẨU CÁ NHÂN
        with st.expander("🔑 Đổi mật khẩu"):
            old_p = st.text_input("Mật khẩu cũ", type="password")
            new_p = st.text_input("Mật khẩu mới", type="password")
            if st.button("Xác nhận đổi", use_container_width=True):
                if old_p == u_info.get("pass"):
                    update_firebase(f"users/{st.session_state.user}", {"pass": new_p, "role": u_info.get("role"), "permissions": perms})
                    st.success("Đã đổi!")
                else: st.error("Sai pass cũ!")

        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚪 ĐĂNG XUẤT", type="primary", use_container_width=True):
            st.session_state.user = None
            st.session_state.is_admin = False
            st.rerun()

    # --- LỌC TABS THEO QUYỀN TRUY CẬP ---
    all_tabs = {"🎯 KPI": "TÍCH LŨY", "🗓️ LỊCH TRỰC": "XEM LỊCH", "💰 QUỸ SHOP": "QUỸ SHOP"}
    allowed_tabs = []
    
    if st.session_state.is_admin: allowed_tabs = list(all_tabs.keys())
    else: allowed_tabs = [k for k, v in all_tabs.items() if v in perms]

    if not allowed_tabs:
        st.error("Tài khoản của bạn chưa được cấp quyền xem bảng nào. Vui lòng liên hệ Admin!")
    else:
        tabs = st.tabs(allowed_tabs)
        
        # --- TAB 1: KPI (HIỂN THỊ DỮ LIỆU THẬT) ---
        if "🎯 KPI" in allowed_tabs:
            with tabs[allowed_tabs.index("🎯 KPI")]:
                st.markdown("<h3 style='color: #0ea5e9;'>Tiến Độ KPI Tháng Này</h3>", unsafe_allow_html=True)
                kpi_data = db.get("kpi", {}).get("emp", {})
                
                if not kpi_data: st.info("Chưa có dữ liệu KPI.")
                else:
                    tot_t = sum(d.get("tgt", 0) for d in kpi_data.values())
                    tot_s = sum(d.get("sold", 0) for d in kpi_data.values())
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Tổng Target", f"{tot_t}")
                    c2.metric("Đã bán", f"{tot_s}")
                    c3.metric("Tiến độ", f"{(tot_s / tot_t * 100) if tot_t > 0 else 0:.1f}%")
                    st.divider()

                    for emp, info in kpi_data.items():
                        tgt = info.get("tgt", 0)
                        sold = info.get("sold", 0)
                        rem = tgt - sold
                        
                        with st.container():
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"**{emp}**")
                                st.progress(sold / tgt if tgt > 0 and sold <= tgt else (1.0 if sold > tgt else 0.0))
                                st.caption(f"Bán: **{sold}** / **{tgt}** (Còn: {rem if rem>0 else 0})")
                            with col2:
                                if st.session_state.is_admin:
                                    n_sold = st.number_input("Sửa", value=sold, step=1, key=f"kpi_{emp}", label_visibility="collapsed")
                                    if n_sold != sold:
                                        update_firebase(f"kpi/emp/{emp}", {"sold": n_sold})
                                        st.rerun()
                                else:
                                    if rem <= 0: st.success("Xong!")
                                    else: st.warning(f"Thiếu {rem}")
                        st.markdown("---")

        # --- TAB 2: LỊCH TRỰC (HIỂN THỊ DỮ LIỆU THẬT) ---
        if "🗓️ LỊCH TRỰC" in allowed_tabs:
            with tabs[allowed_tabs.index("🗓️ LỊCH TRỰC")]:
                st.markdown("<h3 style='color: #0ea5e9;'>Lịch Trực Gần Nhất</h3>", unsafe_allow_html=True)
                history = db.get("detailed_history", {})
                
                if not history: st.info("Chưa có lịch trực.")
                else:
                    for date_str, shifts in history.items():
                        with st.expander(f"📅 {date_str}", expanded=True):
                            st.markdown(f"**☀️ Sáng:** {', '.join(shifts.get('Sáng', [])) if shifts.get('Sáng') else 'Trống'}")
                            st.markdown(f"**🌤️ Chiều:** {', '.join(shifts.get('Chiều', [])) if shifts.get('Chiều') else 'Trống'}")
                            st.markdown(f"**🌙 Tối (10h30):** {', '.join(shifts.get('10h30', [])) if shifts.get('10h30') else 'Trống'}")

        # --- TAB 3: QUỸ SHOP (HIỂN THỊ DỮ LIỆU THẬT) ---
        if "💰 QUỸ SHOP" in allowed_tabs:
            with tabs[allowed_tabs.index("💰 QUỸ SHOP")]:
                st.markdown("<h3 style='color: #0ea5e9;'>Sổ Quỹ Cửa Hàng</h3>", unsafe_allow_html=True)
                qs = db.get("quy_shop", {})
                
                tong_thu = sum(float(i.get("amount", 0)) for i in qs.values() if i.get("type") == "Thu")
                tong_chi = sum(float(i.get("amount", 0)) for i in qs.values() if i.get("type") == "Chi")
                ton_quy = tong_thu - tong_chi
                
                c1, c2, c3 = st.columns(3)
                c1.metric("TỒN QUỸ", format_vnd(ton_quy))
                c2.metric("Tổng Thu", format_vnd(tong_thu))
                c3.metric("Tổng Chi", format_vnd(tong_chi))
                st.divider()
                
                # Form nhập liệu (Chỉ Admin)
                if st.session_state.is_admin:
                    with st.expander("➕ THÊM GIAO DỊCH", expanded=False):
                        with st.form("fund_form", clear_on_submit=True):
                            f_type = st.selectbox("Loại", ["Thu", "Chi"])
                            f_amt = st.number_input("Số tiền", min_value=0, step=50000)
                            f_desc = st.text_input("Lý do / Nội dung")
                            if st.form_submit_button("LƯU VÀO SỔ", use_container_width=True):
                                if f_amt > 0 and f_desc:
                                    tx_id = str(int(time.time() * 1000))
                                    now_str = (datetime.utcnow() + timedelta(hours=7)).strftime("%d/%m/%Y %H:%M")
                                    update_firebase("quy_shop", {tx_id: {"date": now_str, "type": f_type, "amount": f_amt, "desc": f_desc, "user": st.session_state.user}})
                                    st.success("Đã lưu!")
                                    time.sleep(0.5); st.rerun()
                                else: st.error("Nhập đủ số tiền & lý do!")
                else: st.info("💡 Chỉ Admin mới có quyền nhập/xóa sổ quỹ.")
                
                # Lịch sử
                st.markdown("#### 📜 Lịch sử thu chi")
                if not qs: st.caption("Sổ quỹ trống.")
                else:
                    for tid, tx in sorted(qs.items(), key=lambda x: x[0], reverse=True):
                        c1, c2 = st.columns([5, 1])
                        c_color = "#10b981" if tx["type"] == "Thu" else "#ef4444"
                        icon = "➕" if tx["type"] == "Thu" else "➖"
                        
                        with c1:
                            st.markdown(f"**{tx.get('date')}** *(nhập bởi {tx.get('user')})*<br><span style='color:{c_color}; font-size:18px; font-weight:bold;'>{icon} {format_vnd(tx.get('amount', 0))}</span><br>📝 {tx.get('desc')}", unsafe_allow_html=True)
                        with c2:
                            if st.session_state.is_admin:
                                if st.button("❌", key=f"del_{tid}"):
                                    delete_firebase(f"quy_shop/{tid}")
                                    st.rerun()
                        st.markdown("---")
