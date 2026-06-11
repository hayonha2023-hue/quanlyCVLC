import streamlit as st
import requests
import pandas as pd
import time
import hashlib
from datetime import datetime, timedelta

# ==========================================
# CẤU HÌNH GIAO DIỆN
# ==========================================
st.set_page_config(page_title="HTCV by DatTT", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

# CSS MỚI NHẤT: BẢO TOÀN HEADER, CHỈ BẮN TỈA NÚT RÁC
base_css = """
<style>
    /* BẢO TOÀN HEADER ĐỂ NÚT MỞ SIDEBAR LUÔN HOẠT ĐỘNG */
    header { background-color: transparent !important; }
    
    /* CHỈ TIÊU DIỆT CÁC NÚT RÁC BÊN PHẢI (Deploy, Github, 3 chấm) */
    [data-testid="stHeaderActionElements"] {display: none !important;}
    .stDeployButton {display: none !important;}
    #manage-app-button {display: none !important;}
    
    /* ẨN FOOTER VÀ CÁC LOGO STREAMLIT */
    footer {display: none !important;}
    .viewerBadge_container {display: none !important;}
    
    /* THIẾT KẾ FORM & NÚT BẤM */
    [data-testid="stForm"] {
        border-radius: 16px !important;
        border: 1px solid rgba(150, 150, 150, 0.2) !important;
        padding: 20px !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1) !important;
    }
    .stButton>button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    }
    
    /* THIẾT KẾ THẺ METRIC & EXPANDER */
    [data-testid="stMetric"] {
        border-radius: 16px !important;
        padding: 15px 20px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05) !important;
        text-align: center !important;
        border: 1px solid rgba(150, 150, 150, 0.1) !important;
    }
    [data-testid="stExpander"] {
        border-radius: 12px !important;
        overflow: hidden !important;
        border: 1px solid rgba(150, 150, 150, 0.2) !important;
    }

    /* TÙY CHỈNH MENU SIDEBAR XỊN XÒ */
    [data-testid="stSidebar"] div[role="radiogroup"] > label {
        background-color: transparent !important;
        border-radius: 10px !important;
        padding: 12px 15px !important;
        margin-bottom: 8px !important;
        cursor: pointer;
        transition: all 0.2s ease-in-out !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
        background-color: rgba(14, 165, 233, 0.1) !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] {
        background-color: rgba(14, 165, 233, 0.2) !important;
        border-left: 5px solid #0ea5e9 !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {
        display: none !important; /* Ẩn chấm tròn */
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label p {
        font-size: 16px !important;
        font-weight: 600 !important;
    }
</style>
"""
st.markdown(base_css, unsafe_allow_html=True)

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

if "user" not in st.session_state:
    st.session_state.user = None
    st.session_state.is_admin = False
    st.session_state.page = "login"
if "theme" not in st.session_state:
    st.session_state.theme = "Dark" 

db = get_data()

if st.session_state.theme == "Light":
    theme_css = """
    <style>
        [data-testid="stAppViewContainer"] {background-color: #f8fafc !important;} 
        [data-testid="stSidebar"] {background-color: #ffffff !important; border-right: 1px solid #e2e8f0 !important;}
        .stApp {background-color: #f8fafc !important; color: #0f172a !important;} 
        .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, label, span, th, td {color: #1e293b !important;}
        [data-testid="stMetricValue"] {color: #0ea5e9 !important;}
        [data-testid="stMetric"], [data-testid="stForm"], [data-testid="stExpander"] {background-color: #ffffff !important;}
        button[kind="secondary"] { background-color: #ffffff !important; color: #0369a1 !important; border: 1px solid #cbd5e1 !important; }
        button[kind="secondary"]:hover { background-color: #f0f9ff !important; border-color: #0ea5e9 !important; }
    </style>
    """
else:
    theme_css = """
    <style>
        [data-testid="stAppViewContainer"] {background-color: #0b1121 !important;} 
        [data-testid="stSidebar"] {background-color: #162032 !important; border-right: 1px solid #1e293b !important;}
        .stApp {background-color: #0b1121 !important; color: #f8fafc !important;} 
        .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, label, span, th, td {color: #f1f5f9 !important;}
        [data-testid="stMetricValue"] {color: #38bdf8 !important;}
        [data-testid="stMetric"], [data-testid="stForm"], [data-testid="stExpander"] {background-color: #162032 !important;}
        button[kind="secondary"] { background-color: #1e293b !important; color: #38bdf8 !important; border: 1px solid #334155 !important; }
        button[kind="secondary"]:hover { background-color: #0f172a !important; border-color: #38bdf8 !important; }
    </style>
    """
st.markdown(theme_css, unsafe_allow_html=True)

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
            if c1.button("📝 Đăng ký tài khoản", use_container_width=True): st.session_state.page = "register"; st.rerun()
            if c2.button("❓ Quên mật khẩu", use_container_width=True): st.session_state.page = "forgot"; st.rerun()

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
# MÀN HÌNH CHÍNH & SIDEBAR
# ==========================================
else:
    u_info = db.get("users", {}).get(st.session_state.user, {})
    perms = u_info.get("permissions", [])
    
    # Chuẩn bị Danh sách Menu
    tab_dict = {"🎯 KPI": "TÍCH LŨY", "🗓️ LỊCH TRỰC": "XEM LỊCH", "🛒 ECOM": "LỊCH ECOM", "📍 THỊ TRƯỜNG": "THỊ TRƯỜNG", "💰 QUỸ SHOP": "QUỸ SHOP"}
    allowed_tabs = []
    
    if st.session_state.is_admin: 
        allowed_tabs = list(tab_dict.keys()) + ["👥 QUẢN TRỊ ADMIN"]
    else: 
        allowed_tabs = [k for k, v in tab_dict.items() if v in perms]

    if not allowed_tabs:
        st.error("Tài khoản chưa được cấp quyền truy cập. Vui lòng báo Admin!")
        if st.button("Thoát"): logout()
    else:
        # --- THIẾT KẾ SIDEBAR GIAO DIỆN APP ---
        with st.sidebar:
            role_icon = "👑" if st.session_state.is_admin else "👤"
            st.markdown(f"<h2 style='text-align: center; color: #0ea5e9; margin-bottom: 0;'>{role_icon} {st.session_state.user.upper()}</h2>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; color: #64748b; font-size: 13px;'>{ 'Quyền Quản Trị' if st.session_state.is_admin else 'Quyền Nhân Viên' }</p>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Khối chọn chức năng Menu
            selected_tab = st.radio("MENU CHỨC NĂNG", allowed_tabs, label_visibility="collapsed")
            
            st.markdown("<br><hr style='border-color: rgba(150,150,150,0.2);'><br>", unsafe_allow_html=True)
            
            # Cài đặt cá nhân & Công cụ
            if st.button("🔑 Đổi mật khẩu", use_container_width=True):
                st.session_state.show_pass = not st.session_state.get("show_pass", False)
                
            theme_txt = "☀️ Chế độ Sáng" if st.session_state.theme == "Dark" else "🌙 Chế độ Tối"
            if st.button(theme_txt, use_container_width=True):
                st.session_state.theme = "Light" if st.session_state.theme == "Dark" else "Dark"
                st.rerun()
                
            if st.button("🚪 Đăng xuất", use_container_width=True):
                logout()

        # --- KHUNG ĐỔI MẬT KHẨU NỔI (NẾU BẤM TỪ SIDEBAR) ---
        if st.session_state.get("show_pass", False):
            with st.container():
                st.markdown("<div style='padding: 20px; border-radius: 12px; background-color: rgba(14, 165, 233, 0.05); border: 1px solid #0ea5e9; margin-bottom: 20px;'>", unsafe_allow_html=True)
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

        # ==========================================
        # XỬ LÝ HIỂN THỊ NỘI DUNG THEO MENU ĐÃ CHỌN
        # ==========================================
        
        # 1. BẢNG KPI
        if selected_tab == "🎯 KPI":
            st.markdown("<h3 style='margin-top: 0px; margin-bottom: 20px;'>🎯 Tiến Độ KPI Tháng Này</h3>", unsafe_allow_html=True)
            kpi_node = db.get("kpi")
            if not isinstance(kpi_node, dict): kpi_node = {}
            kpi_data = kpi_node.get("emp")
            if isinstance(kpi_data, list):
                kpi_data = {str(i): v for i, v in enumerate(kpi_data) if v is not None}
            elif not isinstance(kpi_data, dict): 
                kpi_data = {}
            
            if not kpi_data: 
                st.info("Chưa có dữ liệu KPI.")
            else:
                tot_t = int(kpi_node.get("tot", 0))
                tot_s = sum(int(d.get("sold", 0)) for d in kpi_data.values() if isinstance(d, dict))
                pct = (tot_s / tot_t * 100) if tot_t > 0 else 0
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Tổng Target", f"{tot_t}")
                c2.metric("Đã bán", f"{tot_s}")
                c3.metric("Hoàn thành", f"{pct:.1f}%")
                st.markdown("<br>", unsafe_allow_html=True)

                kpi_list = []
                for emp, info in kpi_data.items():
                    tgt = info.get("tgt", 0)
                    sold = info.get("sold", 0)
                    rem = tgt - sold if tgt - sold > 0 else 0
                    kpi_list.append({"Nhân Viên": emp, "Đã Bán": sold, "Target": tgt, "Còn Thiếu": rem})
                
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

        # 2. BẢNG LỊCH TRỰC
        elif selected_tab == "🗓️ LỊCH TRỰC":
            st.markdown("<h3 style='margin-top: 0px; margin-bottom: 20px;'>🗓️ Lịch Trực Tuần Gần Nhất</h3>", unsafe_allow_html=True)
            history = db.get("detailed_history", {})
            if not history: 
                st.info("Chưa có lịch trực.")
            else:
                lich_list = []
                for date_str, shifts in history.items():
                    lich_list.append({
                        "Ngày": date_str,
                        "Sáng": ", ".join(shifts.get("Sáng", [])) if shifts.get("Sáng") else "-",
                        "Chiều": ", ".join(shifts.get("Chiều", [])) if shifts.get("Chiều") else "-",
                        "Tối (10h30)": ", ".join(shifts.get("10h30", [])) if shifts.get("10h30") else "-"
                    })
                st.dataframe(pd.DataFrame(lich_list), hide_index=True, use_container_width=True)

        # 3. LỊCH ECOM
        elif selected_tab == "🛒 ECOM":
            st.markdown("<h3 style='margin-top: 0px; margin-bottom: 20px;'>🛒 Lịch Trực ECOM</h3>", unsafe_allow_html=True)
            ecom_data = db.get("ecom_history", {})
            if not ecom_data:
                st.info("Chưa có lịch Ecom.")
            else:
                days = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"]
                ecom_list = []
                for d in days:
                    val = ecom_data.get(d, {})
                    if isinstance(val, str): 
                        if val.strip():
                            ecom_list.append({"Ngày": d, "Sáng": val.strip(), "Chiều": "-"})
                    elif isinstance(val, dict):
                        s = val.get("Sáng", "").strip()
                        c = val.get("Chiều", "").strip()
                        if s or c:
                            ecom_list.append({"Ngày": d, "Sáng": s if s else "-", "Chiều": c if c else "-"})
                        
                if ecom_list:
                    st.dataframe(pd.DataFrame(ecom_list), hide_index=True, use_container_width=True)
                else:
                    st.info("Lịch Ecom đang trống (Chưa có nhân sự nào được điền).")

        # 4. LỊCH THỊ TRƯỜNG
        elif selected_tab == "📍 THỊ TRƯỜNG":
            st.markdown("<h3 style='margin-top: 0px; margin-bottom: 20px;'>📍 Lịch Đi Thị Trường</h3>", unsafe_allow_html=True)
            market_data = db.get("market_history", {})
            if not market_data:
                st.info("Chưa có lịch thị trường.")
            else:
                days_order = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"]
                market_list = []
                for d in days_order:
                    if d in market_data:
                        inf = market_data[d]
                        market_list.append({
                            "Ngày": d,
                            "📍 Địa điểm": inf.get("dia_diem", ""),
                            "👥 Nhân viên": ", ".join(inf.get("nhan_vien", []))
                        })
                        
                if market_list:
                    st.dataframe(pd.DataFrame(market_list), hide_index=True, use_container_width=True)
                else:
                    st.info("Lịch thị trường đang trống.")

        # 5. QUỸ SHOP
        elif selected_tab == "💰 QUỸ SHOP":
            st.markdown("<h3 style='margin-top: 0px; margin-bottom: 20px;'>💰 Quản Lý Sổ Quỹ</h3>", unsafe_allow_html=True)
            qs = db.get("quy_shop", {})
            tong_thu = sum(float(i.get("amount", 0)) for i in qs.values() if i.get("type") == "Thu")
            tong_chi = sum(float(i.get("amount", 0)) for i in qs.values() if i.get("type") == "Chi")
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
                    quy_list.append({
                        "Mã": f"...{tx_id[-4:]}",
                        "Ngày": tx.get("date", ""),
                        "Loại": "➕ Thu" if tx.get("type") == "Thu" else "➖ Chi",
                        "Số Tiền": f"{float(tx.get('amount', 0)):,.0f} ₫".replace(",", "."),
                        "Lý do": tx.get("desc", ""),
                        "Người nhập": tx.get("user", "")
                    })
                st.dataframe(pd.DataFrame(quy_list), hide_index=True, use_container_width=True)
                
                if st.session_state.is_admin:
                    st.caption("Xóa giao dịch (Nếu nhập nhầm):")
                    c_sel, c_del = st.columns([3, 1])
                    xoa_id = c_sel.selectbox("Mã giao dịch:", [tx["Mã"] for tx in quy_list], label_visibility="collapsed")
                    if c_del.button("❌ Xóa", type="primary", use_container_width=True):
                        full_id = [tid for tid in qs.keys() if tid[-4:] == xoa_id[-4:]][0]
                        delete_firebase(f"quy_shop/{full_id}")
                        st.success("Đã xóa!"); time.sleep(0.5); st.rerun()

        # 6. QUẢN TRỊ ADMIN
        elif selected_tab == "👥 QUẢN TRỊ ADMIN":
            st.markdown("<h3 style='margin-top: 0px; margin-bottom: 20px;'>⚙️ Quản Trị Hệ Thống</h3>", unsafe_allow_html=True)
            
            st.markdown("#### ⏳ Yêu Cầu Đăng Ký Mới")
            pending = db.get("pending_users", {})
            if not pending: 
                st.info("Không có yêu cầu chờ.")
            else:
                for pu, pinfo in pending.items():
                    with st.container():
                        c1, c2, c3 = st.columns([4, 2, 2])
                        c1.markdown(f"**👤 {pu}**")
                        if c2.button("✅ Duyệt", key=f"ok_{pu}", type="primary", use_container_width=True):
                            update_firebase(f"users/{pu}", {"pass": pinfo["pass"], "role": "user", "permissions": ["XEM LỊCH", "TÍCH LŨY", "LỊCH ECOM", "THỊ TRƯỜNG"]})
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
                            ["TÍCH LŨY", "XEM LỊCH", "LỊCH ECOM", "THỊ TRƯỜNG", "QUỸ SHOP"], 
                            default=[p for p in current_perms if p in ["TÍCH LŨY", "XEM LỊCH", "LỊCH ECOM", "THỊ TRƯỜNG", "QUỸ SHOP"]],
                            key=f"perm_{u}"
                        )
                        if st.button("💾 Lưu Quyền Mới", key=f"save_{u}", type="primary", use_container_width=True):
                            update_firebase(f"users/{u}/permissions", new_perms)
                            st.success(f"Đã lưu!"); time.sleep(0.5); st.rerun()
