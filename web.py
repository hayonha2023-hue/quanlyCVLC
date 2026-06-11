import streamlit as st
import requests
import pandas as pd
import time
import hashlib
from datetime import datetime, timedelta

# ==========================================
# CẤU HÌNH GIAO DIỆN & SIÊU HIỆU ỨNG CSS
# ==========================================
st.set_page_config(page_title="HTCV by DatTT System", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

base_css = """
<style>
    /* EFFECT 1: HIỆU ỨNG CHUYỂN CẢNH MƯỢT MÀ CHO TOÀN APP */
    @keyframes SAFadeInUp {
        0% { opacity: 0; transform: translateY(12px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    
    [data-testid="stMainBlockContainer"] {
        animation: SAFadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }

    /* BẢO TOÀN HEADER ĐỂ NÚT MỞ SIDEBAR LUÔN HOẠT ĐỘNG */
    header { background-color: transparent !important; }
    [data-testid="stHeaderActionElements"] {display: none !important;}
    .stDeployButton {display: none !important;}
    #manage-app-button {display: none !important;}
    footer {display: none !important;}
    .viewerBadge_container {display: none !important;}
    
    /* EFFECT 2: THIẾT KẾ & HIỆU ỨNG CHO FORM ĐĂNG NHẬP */
    [data-testid="stForm"] {
        border-radius: 20px !important;
        border: 1px solid rgba(150, 150, 150, 0.15) !important;
        padding: 30px !important;
        background: rgba(255, 255, 255, 0.02) !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2) !important;
        transition: all 0.3s ease !important;
    }
    
    /* EFFECT 3: HIỆU ỨNG NÚT BẤM CỰC NHẠY (MICRO-INTERACTIONS) */
    .stButton>button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        letter-spacing: 0.3px !important;
        padding: 10px 20px !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 15px rgba(14, 165, 233, 0.3) !important;
    }
    .stButton>button:active {
        transform: translateY(0px) !important;
    }
    
    /* EFFECT 4: HIỆU ỨNG PHÁT SÁNG NEON VÀ NỔI KHỐI CHO CÁC THẺ TRẠNG THÁI (METRICS) */
    [data-testid="stMetric"] {
        border-radius: 18px !important;
        padding: 20px !important;
        border: 1px solid rgba(14, 165, 233, 0.15) !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-4px) !important;
        border-color: #0ea5e9 !important;
        box-shadow: 0 12px 24px rgba(14, 165, 233, 0.15), 0 0 10px rgba(14, 165, 233, 0.1) !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px !important;
    }
    
    /* BO GÓC MỀM MẠI CHO CÁC HỘP DANH SÁCH MỞ RỘNG */
    [data-testid="stExpander"] {
        border-radius: 14px !important;
        overflow: hidden !important;
        border: 1px solid rgba(150, 150, 150, 0.12) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03) !important;
    }

    /* EFFECT 5: MENU SIDEBAR CAO CẤP NHƯ BIỂU TƯỢNG APP ĐIỆN THOẠI */
    [data-testid="stSidebar"] div[role="radiogroup"] > label {
        background-color: transparent !important;
        border-radius: 12px !important;
        padding: 14px 18px !important;
        margin-bottom: 10px !important;
        cursor: pointer;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
        background-color: rgba(14, 165, 233, 0.08) !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] {
        background-color: rgba(14, 165, 233, 0.15) !important;
        border-left: 5px solid #0ea5e9 !important;
        box-shadow: 0 4px 12px rgba(14, 165, 233, 0.1) !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {
        display: none !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label p {
        font-size: 16px !important;
        font-weight: 600 !important;
        letter-spacing: 0.2px !important;
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

# --- KHỐI MÀU SẮC ĐƯỢC TINH CHỈNH ĐỘ TƯƠNG PHẢN ---
if st.session_state.theme == "Light":
    theme_css = """
    <style>
        [data-testid="stAppViewContainer"] {background-color: #f1f5f9 !important;} 
        [data-testid="stSidebar"] {background-color: #ffffff !important; border-right: 1px solid #e2e8f0 !important;}
        .stApp {background-color: #f1f5f9 !important; color: #0f172a !important;} 
        .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, label, span, th, td {color: #1e293b !important;}
        [data-testid="stMetricValue"] {color: #0284c7 !important;}
        [data-testid="stMetric"], [data-testid="stForm"], [data-testid="stExpander"] {background-color: #ffffff !important;}
        button[kind="secondary"] { background-color: #ffffff !important; color: #0284c7 !important; border: 1px solid #e2e8f0 !important; }
        button[kind="secondary"]:hover { background-color: #f0f9ff !important; border-color: #0ea5e9 !important; }
    </style>
    """
else:
    theme_css = """
    <style>
        [data-testid="stAppViewContainer"] {background-color: #090d16 !important;} 
        [data-testid="stSidebar"] {background-color: #111827 !important; border-right: 1px solid #1f2937 !important;}
        .stApp {background-color: #090d16 !important; color: #f8fafc !important;} 
        .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, label, span, th, td {color: #f1f5f9 !important;}
        [data-testid="stMetricValue"] {color: #38bdf8 !important;}
        [data-testid="stMetric"], [data-testid="stForm"], [data-testid="stExpander"] {background-color: #1f2937 !important;}
        button[kind="secondary"] { background-color: #1f2937 !important; color: #38bdf8 !important; border: 1px solid #374151 !important; }
        button[kind="secondary"]:hover { background-color: #111827 !important; border-color: #38bdf8 !important; }
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
        st.markdown("<h1 style='text-align: center; color: #0ea5e9; font-size: 2.8rem; text-transform: uppercase; letter-spacing: 3px; font-weight:900; text-shadow: 0 0 20px rgba(14,165,233,0.2);'>⚡ HTCV SYSTEM</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; margin-bottom: 40px; opacity: 0.6; font-size:15px; letter-spacing:1px;'>Hệ Thống Quản Lý Số Cửa Hàng Chuyên Nghiệp</p>", unsafe_allow_html=True)
        
        if st.session_state.page == "login":
            with st.form("login_form"):
                st.markdown("<h4 style='text-align: center; margin-bottom: 25px; font-weight:800; letter-spacing:1px;'>XÁC THỰC TÀI KHOẢN</h4>", unsafe_allow_html=True)
                u = st.text_input("👤 TÀI KHOẢN TRUY CẬP").strip().lower()
                p = st.text_input("🔑 MẬT KHẨU BẢO MẬT", type="password")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("🚀 ĐĂNG NHẬP HỆ THỐNG", type="primary", use_container_width=True):
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
                st.markdown("<h4 style='text-align: center; font-weight:800;'>ĐĂNG KÝ TÀI KHOẢN MỚI</h4>", unsafe_allow_html=True)
                new_u = st.text_input("Tên đăng nhập (Viết liền không dấu)").strip().lower()
                new_p = st.text_input("Mật khẩu truy cập", type="password")
                if st.form_submit_button("GỬI YÊU CẦU DUYỆT", type="primary", use_container_width=True):
                    if new_u and new_p:
                        update_firebase("pending_users", {new_u: {"pass": new_p}})
                        st.success("✅ Đã gửi thành công! Vui lòng báo Ban Quản Trị duyệt.")
                    else: st.error("Nhập đủ thông tin!")
            if st.button("⬅ Quay lại đăng nhập", use_container_width=True): st.session_state.page = "login"; st.rerun()

        elif st.session_state.page == "forgot":
            with st.form("forgot_form"):
                st.markdown("<h4 style='text-align: center; font-weight:800;'>KHÔI PHỤC MẬT KHẨU</h4>", unsafe_allow_html=True)
                u = st.text_input("Tài khoản cần khôi phục").strip().lower()
                new_p = st.text_input("Mật khẩu mới muốn cài đặt", type="password")
                secret = st.text_input("Mã xác thực bảo mật cấp cao")
                if st.form_submit_button("XÁC NHẬN THAY ĐỔI", type="primary", use_container_width=True):
                    if secret == "admin123":
                        update_firebase("users", {u: {"pass": new_p}})
                        st.success("✅ Đổi thành công! Vui lòng quay lại đăng nhập.")
                    else: st.error("❌ Mã bảo mật sai!")
            if st.button("⬅ Quay lại đăng nhập", use_container_width=True): st.session_state.page = "login"; st.rerun()

# ==========================================
# MÀN HÌNH CHÍNH & SIDEBAR
# ==========================================
else:
    u_info = db.get("users", {}).get(st.session_state.user, {})
    perms = u_info.get("permissions", [])
    
    tab_dict = {"🎯 BẢNG KPI": "TÍCH LŨY", "🗓️ LỊCH TRỰC": "XEM LỊCH", "🛒 LỊCH ECOM": "LỊCH ECOM", "📍 THI TRƯỜNG": "THỊ TRƯỜNG", "💰 SỔ QUỸ SHOP": "QUỸ SHOP"}
    allowed_tabs = []
    
    if st.session_state.is_admin: 
        allowed_tabs = list(tab_dict.keys()) + ["👥 QUẢN TRỊ ADMIN"]
    else: 
        allowed_tabs = [k for k, v in tab_dict.items() if v in perms]

    if not allowed_tabs:
        st.error("Tài khoản chưa được cấp quyền truy cập. Vui lòng báo Admin!")
        if st.button("Thoát"): logout()
    else:
        with st.sidebar:
            role_icon = "👑" if st.session_state.is_admin else "👤"
            st.markdown(f"<h2 style='text-align: center; color: #0ea5e9; margin-bottom: 0; font-weight:800;'>{role_icon} {st.session_state.user.upper()}</h2>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; color: #64748b; font-size: 13px; font-weight:500; letter-spacing:0.5px;'>{ 'BAN QUẢN TRỊ SYSTEM' if st.session_state.is_admin else 'CƠ SỞ DỮ LIỆU NHÂN VIÊN' }</p>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            selected_tab = st.radio("MENU CHỨC NĂNG", allowed_tabs, label_visibility="collapsed")
            st.markdown("<br><hr style='border-color: rgba(150,150,150,0.1);'><br>", unsafe_allow_html=True)
            
            if st.button("🔑 Cài đặt mật khẩu", use_container_width=True):
                st.session_state.show_pass = not st.session_state.get("show_pass", False)
                
            theme_txt = "☀️ Giao diện Sáng" if st.session_state.theme == "Dark" else "🌙 Giao diện Tối"
            if st.button(theme_txt, use_container_width=True):
                st.session_state.theme = "Light" if st.session_state.theme == "Dark" else "Dark"
                st.rerun()
                
            if st.button("🚪 Đăng xuất tài khoản", use_container_width=True):
                logout()

        if st.session_state.get("show_pass", False):
            with st.container():
                st.markdown("<div style='padding: 22px; border-radius: 16px; background-color: rgba(14, 165, 233, 0.04); border: 1px solid rgba(14, 165, 233, 0.2); margin-bottom: 25px;'>", unsafe_allow_html=True)
                st.markdown("<h5 style='margin-top:0px; color: #0ea5e9; font-weight:700;'>THIẾT LẬP LẠI MẬT KHẨU CÁ NHÂN</h5>", unsafe_allow_html=True)
                cc1, cc2, cc3 = st.columns([3, 3, 2])
                old_p = cc1.text_input("Mật khẩu cũ", type="password", placeholder="Nhập mật khẩu hiện tại...")
                new_p = cc2.text_input("Mật khẩu mới", type="password", placeholder="Nhập mật khẩu mới...")
                cc3.markdown("<div style='padding-top: 28px;'></div>", unsafe_allow_html=True)
                if cc3.button("💾 CẬP NHẬT PASS", type="primary", use_container_width=True):
                    if old_p == u_info.get("pass"):
                        update_firebase(f"users/{st.session_state.user}", {"pass": new_p, "role": u_info.get("role"), "permissions": perms})
                        st.query_params["t"] = get_hash(new_p)
                        st.success("Đã đổi mật khẩu thành công!")
                        st.session_state.show_pass = False
                        time.sleep(1)
                        st.rerun()
                    else: 
                        cc3.error("Sai pass cũ!")
                st.markdown("</div>", unsafe_allow_html=True)

        # ==========================================
        # XỬ LÝ NỘI DUNG FORM
        # ==========================================
        if selected_tab == "🎯 BẢNG KPI":
            st.markdown("<h3 style='margin-top: 0px; margin-bottom: 25px; font-weight:800;'>🎯 Tiến Độ Hoàn Thành KPI Tháng Này</h3>", unsafe_allow_html=True)
            kpi_node = db.get("kpi")
            if not isinstance(kpi_node, dict): kpi_node = {}
            kpi_data = kpi_node.get("emp")
            if isinstance(kpi_data, list):
                kpi_data = {str(i): v for i, v in enumerate(kpi_data) if v is not None}
            elif not isinstance(kpi_data, dict): 
                kpi_data = {}
            
            if not kpi_data: 
                st.info("Chưa có dữ liệu mục tiêu KPI tháng này.")
            else:
                tot_t = int(kpi_node.get("tot", 0))
                tot_s = sum(int(d.get("sold", 0)) for d in kpi_data.values() if isinstance(d, dict))
                pct = (tot_s / tot_t * 100) if tot_t > 0 else 0
                
                c1, c2, c3 = st.columns(3)
                c1.metric("MỤC TIÊU CỬA HÀNG", f"{tot_t:,}".replace(",", "."))
                c2.metric("TỔNG SỐ ĐÃ BÁN", f"{tot_s:,}".replace(",", "."))
                c3.metric("TIẾN ĐỘ HOÀN THÀNH", f"{pct:.1f}%")
                st.markdown("<br>", unsafe_allow_html=True)

                kpi_list = []
                for emp, info in kpi_data.items():
                    tgt = info.get("tgt", 0)
                    sold = info.get("sold", 0)
                    rem = tgt - sold if tgt - sold > 0 else 0
                    kpi_list.append({"Nhân Viên": emp, "Đã Bán (Số lượng)": sold, "Target Giao": tgt, "Còn Thiếu KPI": rem})
                
                df_kpi = pd.DataFrame(kpi_list)

                if st.session_state.is_admin:
                    st.caption("💡 Admin chạm 2 lần vào ô 'Đã Bán (Số lượng)' để sửa nhanh số lượng trực tiếp.")
                    edited_df = st.data_editor(df_kpi, hide_index=True, disabled=["Nhân Viên", "Target Giao", "Còn Thiếu KPI"], use_container_width=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("💾 LƯU SỐ LIỆU SỬA ĐỔI", type="primary", use_container_width=True):
                        for idx, row in edited_df.iterrows():
                            update_firebase(f"kpi/emp/{row['Nhân Viên']}", {"sold": int(row["Đã Bán (Số lượng)"])})
                        st.success("Đã đồng bộ cập nhật lên hệ thống!"); time.sleep(0.5); st.rerun()
                else:
                    st.dataframe(df_kpi, hide_index=True, use_container_width=True)

        elif selected_tab == "🗓️ LỊCH TRỰC":
            st.markdown("<h3 style='margin-top: 0px; margin-bottom: 25px; font-weight:800;'>🗓️ Bảng Phân Phối Lịch Trực Tuần</h3>", unsafe_allow_html=True)
            history = db.get("detailed_history", {})
            if not history: 
                st.info("Chưa có thông tin phân lịch tuần mới.")
            else:
                lich_list = []
                for date_str, shifts in history.items():
                    lich_list.append({
                        "Mốc Thời Gian": date_str,
                        "Ca Sáng": ", ".join(shifts.get("Sáng", [])) if shifts.get("Sáng") else "-",
                        "Ca Chiều": ", ".join(shifts.get("Chiều", [])) if shifts.get("Chiều") else "-",
                        "Ca Đêm (10h30)": ", ".join(shifts.get("10h30", [])) if shifts.get("10h30") else "-"
                    })
                st.dataframe(pd.DataFrame(lich_list), hide_index=True, use_container_width=True)

        elif selected_tab == "🛒 LỊCH ECOM":
            st.markdown("<h3 style='margin-top: 0px; margin-bottom: 25px; font-weight:800;'>🛒 Bảng Phân Phối Ca Trực Khối ECOM</h3>", unsafe_allow_html=True)
            ecom_data = db.get("ecom_history", {})
            if not ecom_data:
                st.info("Lịch trực khối Thương mại điện tử hiện tại trống.")
            else:
                days = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"]
                ecom_list = []
                for d in days:
                    val = ecom_data.get(d, {})
                    if isinstance(val, str): 
                        if val.strip(): ecom_list.append({"Thứ / Ngày": d, "Nhân Sự Trực Sáng": val.strip(), "Nhân Sự Trực Chiều": "-"})
                    elif isinstance(val, dict):
                        s = val.get("Sáng", "").strip()
                        c = val.get("Chiều", "").strip()
                        if s or c: ecom_list.append({"Thứ / Ngày": d, "Nhân Sự Trực Sáng": s if s else "-", "Nhân Sự Trực Chiều": c if c else "-"})
                        
                if ecom_list:
                    st.dataframe(pd.DataFrame(ecom_list), hide_index=True, use_container_width=True)
                else:
                    st.info("Lịch Ecom hiện đang trống (Admin chưa điền nhân sự).")

        elif selected_tab == "📍 THI TRƯỜNG":
            st.markdown("<h3 style='margin-top: 0px; margin-bottom: 25px; font-weight:800;'>📍 Bản Đồ Phân Công Công Tác Thị Trường</h3>", unsafe_allow_html=True)
            market_data = db.get("market_history", {})
            if not market_data:
                st.info("Chưa có lịch phân phối công tác ngoài thị trường.")
            else:
                days_order = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"]
                market_list = []
                for d in days_order:
                    if d in market_data:
                        inf = market_data[d]
                        market_list.append({
                            "Kế hoạch Ngày": d,
                            "📍 Địa Điểm Khảo Sát": inf.get("dia_diem", ""),
                            "👥 Nhân Sự Tuyến Thị Trường": ", ".join(inf.get("nhan_vien", []))
                        })
                        
                if market_list:
                    st.dataframe(pd.DataFrame(market_list), hide_index=True, use_container_width=True)
                else:
                    st.info("Lịch điều phối thị trường đang trống.")

        elif selected_tab == "💰 SỔ QUỸ SHOP":
            st.markdown("<h3 style='margin-top: 0px; margin-bottom: 25px; font-weight:800;'>💰 Sổ Theo Dõi Thu Chi Quỹ Cửa Hàng</h3>", unsafe_allow_html=True)
            qs = db.get("quy_shop", {})
            tong_thu = sum(float(i.get("amount", 0)) for i in qs.values() if i.get("type") == "Thu")
            tong_chi = sum(float(i.get("amount", 0)) for i in qs.values() if i.get("type") == "Chi")
            ton_quy = tong_thu - tong_chi
            
            st.metric("🏦 TỒN QUỸ TIỀN MẶT HIỆN TẠI", format_vnd(ton_quy))
            
            c1, c2 = st.columns(2)
            c1.metric("🟢 TỔNG DÒNG THU", format_vnd(tong_thu))
            c2.metric("🔴 TỔNG DÒNG CHI", format_vnd(tong_chi))
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.session_state.is_admin:
                with st.expander("➕ HÀNH ĐỘNG GHI CHỨNG TỪ THU / CHI MỚI", expanded=False):
                    with st.form("fund_form", clear_on_submit=True):
                        f_type = st.selectbox("Phân loại dòng tiền", ["Thu", "Chi"])
                        f_amt = st.number_input("Giá trị dòng tiền (VNĐ)", min_value=0, step=50000)
                        f_desc = st.text_input("Nội dung diễn giải chi tiết lý do")
                        if st.form_submit_button("LƯU PHIẾU VÀO SỔ GỐC", type="primary", use_container_width=True):
                            if f_amt > 0 and f_desc:
                                tx_id = str(int(time.time() * 1000))
                                now_str = (datetime.utcnow() + timedelta(hours=7)).strftime("%d/%m/%Y %H:%M")
                                update_firebase("quy_shop", {tx_id: {"date": now_str, "type": f_type, "amount": f_amt, "desc": f_desc, "user": st.session_state.user}})
                                st.success("✅ Đã kế toán sổ quỹ thành công!"); time.sleep(0.5); st.rerun()
                            else: st.error("❌ Không được bỏ trống số tiền và lý do!")
            
            st.markdown("#### 📜 Nhật Ký Lịch Sử Phát Sinh Giao Dịch")
            if not qs: 
                st.caption("Chưa có biến động dòng tiền nào được ghi nhận.")
            else:
                quy_list = []
                for tx_id, tx in sorted(qs.items(), key=lambda x: x[0], reverse=True):
                    quy_list.append({
                        "Mã CT": f"...{tx_id[-4:]}",
                        "Thời Gian Ghi Nhập": tx.get("date", ""),
                        "Phân Loại": "➕ Thu Tiền" if tx.get("type") == "Thu" else "➖ Chi Tiền",
                        "Giá Trị": f"{float(tx.get('amount', 0)):,.0f} ₫".replace(",", "."),
                        "Lý Do Phát Sinh": tx.get("desc", ""),
                        "Kế Toán Viên": tx.get("user", "")
                    })
                st.dataframe(pd.DataFrame(quy_list), hide_index=True, use_container_width=True)
                
                if st.session_state.is_admin:
                    st.caption("Hủy chứng từ sai sót (Chỉ dành cho Admin):")
                    c_sel, c_del = st.columns([3, 1])
                    xoa_id = c_sel.selectbox("Chọn mã chứng từ hủy:", [tx["Mã CT"] for tx in quy_list], label_visibility="collapsed")
                    if c_del.button("❌ HỦY CHỨNG TỪ", type="primary", use_container_width=True):
                        full_id = [tid for tid in qs.keys() if tid[-4:] == xoa_id[-4:]][0]
                        delete_firebase(f"quy_shop/{full_id}")
                        st.success("Đã xóa bỏ chứng từ khỏi sổ gốc!"); time.sleep(0.5); st.rerun()

        elif selected_tab == "👥 QUẢN TRỊ ADMIN":
            st.markdown("<h3 style='margin-top: 0px; margin-bottom: 25px; font-weight:800;'>⚙️ Trung Tâm Điều Hành Quản Trị Hệ Thống</h3>", unsafe_allow_html=True)
            
            st.markdown("#### ⏳ Yêu Cầu Cấp Tài Khoản Mới Chờ Duyệt")
            pending = db.get("pending_users", {})
            if not pending: 
                st.info("Hiện không có nhân sự nào đang gửi yêu cầu chờ duyệt đăng ký.")
            else:
                for pu, pinfo in pending.items():
                    with st.container():
                        c1, c2, c3 = st.columns([4, 2, 2])
                        c1.markdown(f"**👤 Nhân viên yêu cầu: {pu}**")
                        if c2.button("✅ Phê duyệt cấp quyền", key=f"ok_{pu}", type="primary", use_container_width=True):
                            update_firebase(f"users/{pu}", {"pass": pinfo["pass"], "role": "user", "permissions": ["XEM LỊCH", "TÍCH LŨY", "LỊCH ECOM", "THỊ TRƯỜNG"]})
                            delete_firebase(f"pending_users/{pu}")
                            st.rerun()
                        if c3.button("❌ Bác bỏ", key=f"rej_{pu}", use_container_width=True):
                            delete_firebase(f"pending_users/{pu}")
                            st.rerun()
            
            st.divider()
            st.markdown("#### 🔑 Phân Quyền Hạn Xem Chức Năng Cho Nhân Sự")
            users = db.get("users", {})
            for u, uinfo in users.items():
                if uinfo.get("role") != "admin":
                    with st.expander(f"👤 Cấu hình bảng quyền: {u}"):
                        current_perms = uinfo.get("permissions", [])
                        new_perms = st.multiselect("Chức năng được phép xem trên điện thoại:", 
                            ["TÍCH LŨY", "XEM LỊCH", "LỊCH ECOM", "THỊ TRƯỜNG", "QUỸ SHOP"], 
                            default=[p for p in current_perms if p in ["TÍCH LŨY", "XEM LỊCH", "LỊCH ECOM", "THỊ TRƯỜNG", "QUỸ SHOP"]],
                            key=f"perm_{u}"
                        )
                        if st.button("💾 KÝ DUYỆT BẢNG QUYỀN", key=f"save_{u}", type="primary", use_container_width=True):
                            update_firebase(f"users/{u}/permissions", new_perms)
                            st.success(f"Đã cập nhật bảng phân quyền cho tài khoản {u}!"); time.sleep(0.5); st.rerun()
