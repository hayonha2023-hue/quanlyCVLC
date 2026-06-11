import streamlit as st
import requests
import pandas as pd
import time
import hashlib
from datetime import datetime, timedelta

# ==========================================
# CẤU HÌNH GIAO DIỆN & TIÊU DIỆT NÚT THỪA
# ==========================================
st.set_page_config(page_title="HTCV by DatTT System", page_icon="⚡", layout="wide")

# CSS CƠ BẢN: ẨN MENU RÁC & NÚT MANAGE APP
base_css = """
<style>
    /* Ẩn rác mặc định của Streamlit */
    header {visibility: hidden !important; display: none !important;}
    footer {visibility: hidden !important; display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}
    
    /* Diệt nút Manage App */
    .stDeployButton {display: none !important;}
    [data-testid="manage-app-button"] {display: none !important;}
    #manage-app-button {display: none !important;}
    .viewerBadge_container {display: none !important;}
    .viewerBadge_link {display: none !important;}
    iframe[title*="streamlit"] {display: none !important;}
    div[class^="st-emotion-cache-"] > a[href*="streamlit"] {display: none !important;}
    
    /* Thiết kế form đăng nhập bo góc đẹp */
    [data-testid="stForm"] {
        border-radius: 16px !important;
        border: 1px solid rgba(150, 150, 150, 0.2) !important;
        padding: 20px !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Tối ưu hiệu ứng nút bấm (Nổi lên khi di chuột) */
    .stButton>button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
        transition: all 0.3s ease !important;
        border: none !important;
    }
    .stButton>button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 7px 14px rgba(0,0,0,0.15) !important;
        filter: brightness(1.1);
    }
    
    /* Thiết kế thẻ Metric (Tổng thu, Tồn quỹ) */
    [data-testid="stMetric"] {
        border-radius: 16px !important;
        padding: 15px 20px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05) !important;
        text-align: center !important;
        border: 1px solid rgba(150, 150, 150, 0.1) !important;
    }
    
    /* Bo góc các Expander (Mở rộng) */
    [data-testid="stExpander"] {
        border-radius: 12px !important;
        overflow: hidden !important;
        border: 1px solid rgba(150, 150, 150, 0.2) !important;
    }
    
    /* Làm đẹp thanh Tabs */
    button[data-baseweb="tab"] {
        font-size: 16px !important;
        font-weight: 600 !important;
        border-radius: 8px 8px 0 0 !important;
        padding-bottom: 12px !important;
        padding-top: 12px !important;
    }
</style>
"""
st.markdown(base_css, unsafe_allow_html=True)

# ==========================================
# KẾT NỐI FIREBASE & HÀM TIỆN ÍCH
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

def get_hash(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def logout():
    st.session_state.user = None
    st.session_state.is_admin = False
    st.query_params.clear()
    st.rerun()

# --- KHỞI TẠO SESSION ---
if "user" not in st.session_state:
    st.session_state.user = None
    st.session_state.is_admin = False
    st.session_state.page = "login"
if "theme" not in st.session_state:
    st.session_state.theme = "Dark" # Mặc định nền tối sang trọng

db = get_data()

# --- ÉP MÀU UI CHO SÁNG/TỐI (CARD DESIGN) ---
if st.session_state.theme == "Light":
    theme_css = """
    <style>
        [data-testid="stAppViewContainer"] {background-color: #f8fafc !important;} /* Nền ghi xám nhạt Apple */
        .stApp {background-color: #f8fafc !important; color: #0f172a !important;} 
        .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, label, span, th, td {color: #1e293b !important;}
        div[data-baseweb="tab-list"] button {color: #64748b !important;}
        div[data-baseweb="tab-list"] button[aria-selected="true"] {color: #0ea5e9 !important; border-bottom: 3px solid #0ea5e9 !important;}
        [data-testid="stMetricValue"] {color: #0ea5e9 !important;}
        [data-testid="stMetric"] {background-color: #ffffff !important;} /* Thẻ trắng tinh */
        [data-testid="stForm"] {background-color: #ffffff !important;}
        [data-testid="stExpander"] {background-color: #ffffff !important;}
    </style>
    """
else:
    theme_css = """
    <style>
        [data-testid="stAppViewContainer"] {background-color: #0b1121 !important;} /* Nền xanh navy cực đậm */
        .stApp {background-color: #0b1121 !important; color: #f8fafc !important;} 
        .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, label, span, th, td {color: #f1f5f9 !important;}
        div[data-baseweb="tab-list"] button {color: #94a3b8 !important;}
        div[data-baseweb="tab-list"] button[aria-selected="true"] {color: #38bdf8 !important; border-bottom: 3px solid #38bdf8 !important;}
        [data-testid="stMetricValue"] {color: #38bdf8 !important;}
        [data-testid="stMetric"] {background-color: #1e293b !important;} /* Thẻ nổi bật trên nền đậm */
        [data-testid="stForm"] {background-color: #162032 !important;}
        [data-testid="stExpander"] {background-color: #162032 !important;}
    </style>
    """
st.markdown(theme_css, unsafe_allow_html=True)

# ==========================================
# CƠ CHẾ ĐĂNG NHẬP TỰ ĐỘNG
# ==========================================
if st.session_state.user is None:
    if "u" in st.query_params and "t" in st.query_params:
        u_url = st.query_params["u"]
        t_url = st.query_params["t"]
        users_db = db.get("users", {})
        if u_url in users_db and get_hash(users_db[u_url]["pass"]) == t_url:
            st.session_state.user = u_url
            st.session_state.is_admin = (users_db[u_url].get("role") == "admin")

# ==========================================
# MÀN HÌNH ĐĂNG NHẬP / ĐĂNG KÝ
# ==========================================
if st.session_state.user is None:
    # Căn giữa siêu đẹp trên điện thoại
    _, col_center, _ = st.columns([1, 10, 1])
    with col_center:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: #0ea5e9; font-size: 2.5rem; text-transform: uppercase; letter-spacing: 2px;'>⚡ HTCV</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; margin-bottom: 30px; opacity: 0.8;'>Hệ Thống Quản Lý Thông Minh</p>", unsafe_allow_html=True)
        
        if st.session_state.page == "login":
            with st.form("login_form"):
                st.markdown("<h4 style='text-align: center; margin-bottom: 20px;'>ĐĂNG NHẬP</h4>", unsafe_allow_html=True)
                u = st.text_input("👤 Tài khoản").strip().lower()
                p = st.text_input("🔑 Mật khẩu", type="password")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("🚀 VÀO HỆ THỐNG", type="primary", use_container_width=True):
                    users = db.get("users", {})
                    if u in users and users[u]["pass"] == p:
                        st.session_state.user = u
                        st.session_state.is_admin = (users[u].get("role") == "admin")
                        st.query_params["u"] = u
                        st.query_params["t"] = get_hash(p)
                        st.rerun()
                    elif u in db.get("pending_users", {}): st.warning("⏳ Tài khoản đang chờ Admin duyệt!")
                    else: st.error("❌ Sai thông tin đăng nhập!")
                    
            c1, c2 = st.columns(2)
            if c1.button("📝 Đăng ký", use_container_width=True): st.session_state.page = "register"; st.rerun()
            if c2.button("❓ Quên pass", use_container_width=True): st.session_state.page = "forgot"; st.rerun()

        elif st.session_state.page == "register":
            with st.form("reg_form"):
                st.markdown("<h4 style='text-align: center;'>ĐĂNG KÝ MỚI</h4>", unsafe_allow_html=True)
                new_u = st.text_input("Tên đăng nhập (Viết liền không dấu)").strip().lower()
                new_p = st.text_input("Mật khẩu", type="password")
                if st.form_submit_button("GỬI YÊU CẦU", type="primary", use_container_width=True):
                    if new_u and new_p:
                        update_firebase("pending_users", {new_u: {"pass": new_p}})
                        st.success("✅ Đã gửi! Vui lòng báo Admin duyệt.")
                    else: st.error("Nhập đủ thông tin!")
            if st.button("⬅ Quay lại", use_container_width=True): st.session_state.page = "login"; st.rerun()

        elif st.session_state.page == "forgot":
            with st.form("forgot_form"):
                st.markdown("<h4 style='text-align: center;'>KHÔI PHỤC MẬT KHẨU</h4>", unsafe_allow_html=True)
                u = st.text_input("Tài khoản của bạn").strip().lower()
                new_p = st.text_input("Mật khẩu mới", type="password")
                secret = st.text_input("Mã bảo mật (Hỏi Admin)")
                if st.form_submit_button("ĐỔI MẬT KHẨU", type="primary", use_container_width=True):
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
    
# --- THANH ĐIỀU HƯỚNG MỚI (TỐI ƯU GIAO DIỆN) ---
        c_name, c_pass, c_space, c_theme, c_logout = st.columns([3.5, 2.5, 4.5, 0.75, 0.75])
        
        with c_name:
            role_icon = "👑" if st.session_state.is_admin else "👤"
            st.markdown(f"<h3 style='margin-bottom:0px; padding-top: 5px; color: #0ea5e9;'>{role_icon} {st.session_state.user.upper()}</h3>", unsafe_allow_html=True)
            
        with c_pass:
            st.markdown("<div style='padding-top: 5px;'></div>", unsafe_allow_html=True)
            # Nút cài đặt cá nhân nằm ngay cạnh tên Admin
            if st.button("🔑 Cài đặt cá nhân", use_container_width=True):
                st.session_state.show_pass = not st.session_state.get("show_pass", False)
                
        with c_theme:
            st.markdown("<div style='padding-top: 5px;'></div>", unsafe_allow_html=True)
            # Icon Đổi màu siêu sáng, đẩy tít góc phải
            theme_ico = "☀️" if st.session_state.theme == "Dark" else "🌙"
            if st.button(theme_ico, use_container_width=True):
                st.session_state.theme = "Light" if st.session_state.theme == "Dark" else "Dark"
                st.rerun()
                
        with c_logout:
            st.markdown("<div style='padding-top: 5px;'></div>", unsafe_allow_html=True)
            # Nút thoát cực kỳ gọn nhẹ chỉ có icon
            if st.button("🚪", use_container_width=True):
                logout()

        # Khung đổi mật khẩu hiển thị mượt mà ngay dưới thanh công cụ
        if st.session_state.get("show_pass", False):
            with st.container():
                st.markdown("<div style='padding: 20px; border-radius: 12px; background-color: rgba(14, 165, 233, 0.05); border: 1px solid #0ea5e9; margin-top: 10px;'>", unsafe_allow_html=True)
                st.markdown("<h5 style='margin-top:0px; color: #0ea5e9;'>Đổi mật khẩu bảo mật</h5>", unsafe_allow_html=True)
                
                cc1, cc2, cc3 = st.columns([3, 3, 2])
                old_p = cc1.text_input("Mật khẩu cũ", type="password", placeholder="Nhập mật khẩu hiện tại...")
                new_p = cc2.text_input("Mật khẩu mới", type="password", placeholder="Nhập mật khẩu mới...")
                
                cc3.markdown("<div style='padding-top: 28px;'></div>", unsafe_allow_html=True)
                if cc3.button("💾 Lưu Pass Mới", type="primary", use_container_width=True):
                    if old_p == u_info.get("pass"):
                        update_firebase(f"users/{st.session_state.user}", {"pass": new_p, "role": u_info.get("role"), "permissions": perms})
                        st.query_params["t"] = get_hash(new_p)
                        st.success("Đổi thành công!")
                        st.session_state.show_pass = False
                        time.sleep(1)
                        st.rerun()
                    else: 
                        cc3.error("Sai pass cũ!")
                st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

        # Khung đổi mật khẩu hiển thị mượt mà ngay dưới thanh công cụ
        if st.session_state.get("show_pass", False):
            with st.container():
                st.markdown("<div style='padding: 20px; border-radius: 12px; background-color: rgba(14, 165, 233, 0.05); border: 1px solid #0ea5e9; margin-top: 10px;'>", unsafe_allow_html=True)
                st.markdown("<h5 style='margin-top:0px; color: #0ea5e9;'>Đổi mật khẩu bảo mật</h5>", unsafe_allow_html=True)
                
                cc1, cc2, cc3 = st.columns([3, 3, 2])
                old_p = cc1.text_input("Mật khẩu cũ", type="password", placeholder="Nhập mật khẩu hiện tại...")
                new_p = cc2.text_input("Mật khẩu mới", type="password", placeholder="Nhập mật khẩu mới...")
                
                cc3.markdown("<div style='padding-top: 28px;'></div>", unsafe_allow_html=True)
                if cc3.button("💾 Lưu Pass Mới", type="primary", use_container_width=True):
                    if old_p == u_info.get("pass"):
                        update_firebase(f"users/{st.session_state.user}", {"pass": new_p, "role": u_info.get("role"), "permissions": perms})
                        st.query_params["t"] = get_hash(new_p)
                        st.success("Đổi thành công!")
                        st.session_state.show_pass = False
                        time.sleep(1)
                        st.rerun()
                    else: 
                        cc3.error("Sai pass cũ!")
                st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
    # --- LỌC TABS DỰA TRÊN QUYỀN ---
    tab_dict = {"🎯 KPI": "TÍCH LŨY", "🗓️ LỊCH": "XEM LỊCH", "💰 QUỸ": "QUỸ SHOP"}
    allowed_tabs = []
    
    if st.session_state.is_admin: 
        allowed_tabs = list(tab_dict.keys()) + ["👥 ADMIN"]
    else: 
        allowed_tabs = [k for k, v in tab_dict.items() if v in perms]

    if not allowed_tabs:
        st.error("Tài khoản chưa được cấp quyền truy cập. Báo Admin!")
    else:
        tabs = st.tabs(allowed_tabs)
        
        # ==========================================
        # TAB 1: BẢNG KPI
        # ==========================================
        if "🎯 KPI" in allowed_tabs:
            with tabs[allowed_tabs.index("🎯 KPI")]:
                st.markdown("<h3 style='margin-top: 10px; margin-bottom: 20px;'>🎯 Tiến Độ KPI Tháng Này</h3>", unsafe_allow_html=True)
                
                # --- ÉP KIỂU & CHỐNG LỖI FIREBASE BIẾN TÊN SỐ THÀNH MẢNG ---
                kpi_node = db.get("kpi")
                if not isinstance(kpi_node, dict): kpi_node = {}
                
                kpi_data = kpi_node.get("emp")
                if isinstance(kpi_data, list):
                    # Dịch ngược mảng về lại tên số cho bản Web
                    kpi_data = {str(i): v for i, v in enumerate(kpi_data) if v is not None}
                elif not isinstance(kpi_data, dict): 
                    kpi_data = {}
                
                if not kpi_data: 
                    st.info("Chưa có dữ liệu KPI.")
                else:
                    tot_t = 0
                    tot_s = 0
                    kpi_list = []
                    
                    for emp, info in kpi_data.items():
                        if not isinstance(info, dict): continue
                        tgt = info.get("tgt", 0)
                        sold = info.get("sold", 0)
                        tot_t += tgt
                        tot_s += sold
                        rem = tgt - sold if tgt - sold > 0 else 0
                        kpi_list.append({"Nhân Viên": emp, "Đã Bán": sold, "Target": tgt, "Còn Thiếu": rem})
                        
                    pct = (tot_s / tot_t * 100) if tot_t > 0 else 0
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Tổng Target", f"{tot_t}")
                    c2.metric("Đã bán", f"{tot_s}")
                    c3.metric("Hoàn thành", f"{pct:.1f}%")
                    st.markdown("<br>", unsafe_allow_html=True)

                    if kpi_list:
                        df_kpi = pd.DataFrame(kpi_list)

                        if st.session_state.is_admin:
                            st.caption("💡 Chạm 2 lần vào ô 'Đã Bán' để sửa nhanh số lượng.")
                            edited_df = st.data_editor(df_kpi, hide_index=True, disabled=["Nhân Viên", "Target", "Còn Thiếu"], use_container_width=True)
                            st.markdown("<br>", unsafe_allow_html=True)
                            if st.button("💾 LƯU CẬP NHẬT KPI", type="primary", use_container_width=True):
                                for idx, row in edited_df.iterrows():
                                    update_firebase(f"kpi/emp/{row['Nhân Viên']}", {"sold": int(row["Đã Bán"])})
                                st.success("Đã lưu!"); time.sleep(0.5); st.rerun()
                        else:
                            st.dataframe(df_kpi, hide_index=True, use_container_width=True)

        # ==========================================
        # TAB 2: BẢNG LỊCH TRỰC
        # ==========================================
        if "🗓️ LỊCH" in allowed_tabs:
            with tabs[allowed_tabs.index("🗓️ LỊCH")]:
                st.markdown("<h3 style='margin-top: 10px; margin-bottom: 20px;'>🗓️ Lịch Trực Tuần Gần Nhất</h3>", unsafe_allow_html=True)
                
                # --- ÉP KIỂU AN TOÀN TUYỆT ĐỐI ---
                history = db.get("detailed_history")
                if not isinstance(history, dict): history = {}
                
                if not history: 
                    st.info("Chưa có lịch trực.")
                else:
                    lich_list = []
                    for date_str, shifts in history.items():
                        if not isinstance(shifts, dict): continue
                        lich_list.append({
                            "Ngày": date_str,
                            "Sáng": ", ".join(shifts.get("Sáng", [])) if isinstance(shifts.get("Sáng"), list) else "-",
                            "Chiều": ", ".join(shifts.get("Chiều", [])) if isinstance(shifts.get("Chiều"), list) else "-",
                            "Tối (10h30)": ", ".join(shifts.get("10h30", [])) if isinstance(shifts.get("10h30"), list) else "-"
                        })
                    if lich_list:
                        st.dataframe(pd.DataFrame(lich_list), hide_index=True, use_container_width=True)

        # ==========================================
        # TAB 3: QUỸ SHOP
        # ==========================================
        if "💰 QUỸ" in allowed_tabs:
            with tabs[allowed_tabs.index("💰 QUỸ")]:
                st.markdown("<h3 style='margin-top: 10px; margin-bottom: 20px;'>💰 Quản Lý Sổ Quỹ</h3>", unsafe_allow_html=True)
                
                # --- ÉP KIỂU AN TOÀN TUYỆT ĐỐI ---
                qs = db.get("quy_shop")
                if not isinstance(qs, dict): qs = {}
                
                tong_thu = sum(float(i.get("amount", 0)) for i in qs.values() if isinstance(i, dict) and i.get("type") == "Thu")
                tong_chi = sum(float(i.get("amount", 0)) for i in qs.values() if isinstance(i, dict) and i.get("type") == "Chi")
                ton_quy = tong_thu - tong_chi
                
                st.metric("🏦 HIỆN TẠI TỒN QUỸ", format_vnd(ton_quy))
                
                c1, c2 = st.columns(2)
                c1.metric("🟢 Tổng Thu", format_vnd(tong_thu))
                c2.metric("🔴 Tổng Chi", format_vnd(tong_chi))
                st.markdown("<br>", unsafe_allow_html=True)
                
                if st.session_state.is_admin:
                    with st.expander("➕ GHI SỔ THU / CHI MỚI", expanded=False):
                        with st.form("fund_form", clear_on_submit=True):
                            f_type = st.selectbox("Loại Phiếu", ["Thu", "Chi"])
                            f_amt = st.number_input("Số tiền (VNĐ)", min_value=0, step=50000)
                            f_desc = st.text_input("Ghi chú / Lý do")
                            if st.form_submit_button("LƯU VÀO SỔ QUỸ", type="primary", use_container_width=True):
                                if f_amt > 0 and f_desc:
                                    tx_id = str(int(time.time() * 1000))
                                    now_str = (datetime.utcnow() + timedelta(hours=7)).strftime("%d/%m/%Y %H:%M")
                                    update_firebase("quy_shop", {tx_id: {"date": now_str, "type": f_type, "amount": f_amt, "desc": f_desc, "user": st.session_state.user}})
                                    st.success("✅ Đã lưu!"); time.sleep(0.5); st.rerun()
                                else: st.error("❌ Nhập đủ số tiền và lý do!")
                
                st.markdown("#### 📜 Lịch Sử Thu Chi Gần Đây")
                if not qs: 
                    st.caption("Sổ quỹ trống.")
                else:
                    quy_list = []
                    for tx_id, tx in sorted(qs.items(), key=lambda x: x[0], reverse=True):
                        if not isinstance(tx, dict): continue
                        quy_list.append({
                            "Mã": f"...{str(tx_id)[-4:]}",
                            "Ngày": tx.get("date", ""),
                            "Loại": "➕ Thu" if tx.get("type") == "Thu" else "➖ Chi",
                            "Số Tiền": f"{float(tx.get('amount', 0)):,.0f} ₫".replace(",", "."),
                            "Lý do": tx.get("desc", ""),
                            "Người nhập": tx.get("user", "")
                        })
                    if quy_list:
                        st.dataframe(pd.DataFrame(quy_list), hide_index=True, use_container_width=True)
                        
                        if st.session_state.is_admin:
                            st.caption("Xóa giao dịch (Nếu nhập nhầm):")
                            c_sel, c_del = st.columns([3, 1])
                            xoa_id = c_sel.selectbox("Mã giao dịch:", [tx["Mã"] for tx in quy_list], label_visibility="collapsed")
                            if c_del.button("❌ Xóa", type="primary", use_container_width=True):
                                full_id = [tid for tid in qs.keys() if str(tid)[-4:] == str(xoa_id)[-4:]][0]
                                delete_firebase(f"quy_shop/{full_id}")
                                st.success("Đã xóa!"); time.sleep(0.5); st.rerun()
        # TAB 4: ADMIN (PHÂN QUYỀN)
        # ==========================================
        if "👥 ADMIN" in allowed_tabs:
            with tabs[allowed_tabs.index("👥 ADMIN")]:
                st.markdown("<h3 style='margin-top: 10px; margin-bottom: 20px;'>⚙️ Quản Trị Hệ Thống</h3>", unsafe_allow_html=True)
                
                st.markdown("#### ⏳ Yêu Cầu Đăng Ký Mới")
                pending = db.get("pending_users", {})
                if not pending: st.info("Không có yêu cầu chờ.")
                else:
                    for pu, pinfo in pending.items():
                        with st.container():
                            c1, c2, c3 = st.columns([4, 2, 2])
                            c1.markdown(f"**👤 {pu}**")
                            if c2.button("✅ Duyệt", key=f"ok_{pu}", type="primary", use_container_width=True):
                                update_firebase(f"users/{pu}", {"pass": pinfo["pass"], "role": "user", "permissions": ["XEM LỊCH", "TÍCH LŨY"]})
                                delete_firebase(f"pending_users/{pu}")
                                st.rerun()
                            if c3.button("❌ Bỏ", key=f"rej_{pu}", use_container_width=True):
                                delete_firebase(f"pending_users/{pu}")
                                st.rerun()
                
                st.divider()
                st.markdown("#### 🔑 Phân Quyền Nhân Viên")
                users = db.get("users", {})
                for u, uinfo in users.items():
                    if uinfo.get("role") != "admin":
                        with st.expander(f"👤 Cấp quyền: {u}"):
                            current_perms = uinfo.get("permissions", [])
                            new_perms = st.multiselect("Chức năng được xem:", 
                                ["TÍCH LŨY", "XEM LỊCH", "QUỸ SHOP"], 
                                default=[p for p in current_perms if p in ["TÍCH LŨY", "XEM LỊCH", "QUỸ SHOP"]],
                                key=f"perm_{u}"
                            )
                            if st.button("💾 Lưu Quyền Mới", key=f"save_{u}", type="primary", use_container_width=True):
                                update_firebase(f"users/{u}/permissions", new_perms)
                                st.success(f"Đã lưu!"); time.sleep(0.5); st.rerun()
