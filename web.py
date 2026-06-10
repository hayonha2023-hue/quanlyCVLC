import streamlit st
import requests
import pandas as pd
import time
import hashlib
from datetime import datetime, timedelta

# ==========================================
# CẤU HÌNH GIAO DIỆN & TÀNG HÌNH NÚT THỪA
# ==========================================
st.set_page_config(page_title="HTCV System", page_icon="⚡", layout="wide")

# CSS "HỦY DIỆT DIỆN RỘNG" - KHÓA CHẾT MANAGE APP VÀ ICON RÁC TRÊN ĐIỆN THOẠI
custom_css = """
<style>
    /* Xóa Header và Footer mặc định */
    header {visibility: hidden !important; display: none !important;}
    footer {visibility: hidden !important; display: none !important;}
    
    /* Xóa thanh công cụ góc phải trên */
    [data-testid="stToolbar"] {display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}
    
    /* DIỆT TẬN GỐC NÚT MANAGE APP & BIỂU TƯỢNG NỔI TRÊN ĐIỆN THOẠI */
    .stDeployButton {display: none !important;}
    [data-testid="manage-app-button"] {display: none !important;}
    #manage-app-button {display: none !important;}
    .viewerBadge_container {display: none !important;}
    .viewerBadge_link {display: none !important;}
    iframe[title*="streamlit"] {display: none !important;}
    div[class^="st-emotion-cache-"] > a[href*="streamlit"] {display: none !important;}
    
    /* Tối ưu nút bấm full-width trên giao diện điện thoại */
    .stButton>button {
        width: 100% !important;
        border-radius: 8px !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# KẾT NỐI CƠ SỞ DỮ LIỆU & HÀM TIỆN ÍCH
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

# Khởi tạo Session
if "user" not in st.session_state:
    st.session_state.user = None
    st.session_state.is_admin = False
    st.session_state.page = "login"
if "theme" not in st.session_state:
    st.session_state.theme = "Dark" # Mặc định nền tối OLED

db = get_data()

# --- ÉP GIAO DIỆN SÁNG TỐI THEO YÊU CẦU (MÀU ĐEN OLED CHUẨN ĐÊM) ---
if st.session_state.theme == "Light":
    theme_css = """
    <style>
        [data-testid="stAppViewContainer"] {background-color: #f1f5f9 !important;}
        .stApp {background-color: #f1f5f9 !important; color: #0f172a !important;} 
        .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, label, span, th, td {color: #0f172a !important;}
        div[data-baseweb="tab-list"] button {color: #0f172a !important;}
        div[data-testid="stMetricValue"] {color: #0ea5e9 !important;}
    </style>
    """
else:
    theme_css = """
    <style>
        [data-testid="stAppViewContainer"] {background-color: #000000 !important;}
        .stApp {background-color: #000000 !important; color: #ffffff !important;} 
        .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, label, span, th, td {color: #ffffff !important;}
        div[data-baseweb="tab-list"] button {color: #ffffff !important;}
        div[data-testid="stMetricValue"] {color: #0ea5e9 !important;}
        div[data-testid="stExpander"] {background-color: #111111 !important; border-color: #333333 !important;}
        div[data-testid="stForm"] {background-color: #111111 !important; border-color: #333333 !important;}
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
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #0ea5e9;'>⚡ HTCV SYSTEM</h1>", unsafe_allow_html=True)
    
    if st.session_state.page == "login":
        with st.form("login_form"):
            u = st.text_input("👤 Tài khoản").strip().lower()
            p = st.text_input("🔑 Mật khẩu", type="password")
            if st.form_submit_button("🚀 ĐĂNG NHẬP", use_container_width=True):
                users = db.get("users", {})
                if u in users and users[u]["pass"] == p:
                    st.session_state.user = u
                    st.session_state.is_admin = (users[u].get("role") == "admin")
                    st.query_params["u"] = u
                    st.query_params["t"] = get_hash(p)
                    st.rerun()
                elif u in db.get("pending_users", {}): st.warning("⏳ Tài khoản đang chờ Admin duyệt!")
                else: st.error("❌ Sai thông tin đăng nhập!")
                
        col1, col2 = st.columns(2)
        if col1.button("📝 Đăng ký", use_container_width=True): st.session_state.page = "register"; st.rerun()
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
    
    # --- THANH ĐIỀU HƯỚNG ĐÃ ĐƯỢC TỐI ƯU CHIỀU DỌC CHO ĐIỆN THOẠI ---
    role_txt = "👑 Admin" if st.session_state.is_admin else "👤 NV"
    st.markdown(f"<h3 style='color: #0ea5e9; text-align: center;'>{role_txt}: {st.session_state.user.upper()}</h3>", unsafe_allow_html=True)
    
    # NÚT GẠT ĐỔI MÀU GIAO DIỆN KHÔNG DÙNG CỘT - BAO LÊN ĐIỆN THOẠI CHUẨN 100%
    current_is_light = (st.session_state.theme == "Light")
    toggle_light = st.toggle("🌞 Bật chế độ Nền Sáng / 🌙 Tắt để dùng Nền Đen OLED", value=current_is_light)
    
    if toggle_light != current_is_light:
        st.session_state.theme = "Light" if toggle_light else "Dark"
        st.rerun()
        
    if st.button("🚪 ĐĂNG XUẤT HỆ THỐNG", type="secondary"):
        logout()
            
    with st.expander("🔑 Thay đổi mật khẩu cá nhân"):
        old_p = st.text_input("Mật khẩu cũ", type="password", placeholder="Mật khẩu cũ")
        new_p = st.text_input("Mật khẩu mới", type="password", placeholder="Mật khẩu mới")
        if st.button("Xác nhận đổi pass mới"):
            if old_p == u_info.get("pass"):
                update_firebase(f"users/{st.session_state.user}", {"pass": new_p, "role": u_info.get("role"), "permissions": perms})
                st.query_params["t"] = get_hash(new_p)
                st.success("Đổi thành công!")
            else: st.error("Sai pass cũ!")

    st.divider()

    # --- LỌC TABS DỰA TRÊN QUYỀN ---
    tab_dict = {"🎯 KPI": "TÍCH LŨY", "🗓️ LỊCH TRỰC": "XEM LỊCH", "💰 QUỸ SHOP": "QUỸ SHOP"}
    allowed_tabs = []
    
    if st.session_state.is_admin: 
        allowed_tabs = list(tab_dict.keys()) + ["👥 QUẢN LÝ TÀI KHOẢN"]
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
                st.markdown("### 🎯 Tiến Độ KPI Tháng Này")
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

                    kpi_list = []
                    for emp, info in kpi_data.items():
                        tgt = info.get("tgt", 0)
                        sold = info.get("sold", 0)
                        rem = tgt - sold if tgt - sold > 0 else 0
                        kpi_list.append({"Nhân Viên": emp, "Đã Bán": sold, "Target": tgt, "Còn Thiếu": rem})
                    
                    df_kpi = pd.DataFrame(kpi_list)

                    if st.session_state.is_admin:
                        st.caption("💡 Chạm 2 lần vào số 'Đã Bán' để sửa, sau đó bấm Lưu.")
                        edited_df = st.data_editor(df_kpi, hide_index=True, disabled=["Nhân Viên", "Target", "Còn Thiếu"], use_container_width=True)
                        if st.button("💾 LƯU BẢNG KPI", type="primary"):
                            for idx, row in edited_df.iterrows():
                                update_firebase(f"kpi/emp/{row['Nhân Viên']}", {"sold": int(row["Đã Bán"])})
                            st.success("Đã lưu!"); time.sleep(0.5); st.rerun()
                    else:
                        st.dataframe(df_kpi, hide_index=True, use_container_width=True)

        # ==========================================
        # TAB 2: BẢNG LỊCH TRỰC
        # ==========================================
        if "🗓️ LỊCH TRỰC" in allowed_tabs:
            with tabs[allowed_tabs.index("🗓️ LỊCH TRỰC")]:
                st.markdown("### 🗓️ Lịch Trực Tuần Gần Nhất")
                history = db.get("detailed_history", {})
                if not history: st.info("Chưa có lịch trực.")
                else:
                    lich_list = []
                    for date_str, shifts in history.items():
                        lich_list.append({
                            "Ngày": date_str,
                            "Sáng": ", ".join(shifts.get("Sáng", [])) if shifts.get("Sáng") else "Trống",
                            "Chiều": ", ".join(shifts.get("Chiều", [])) if shifts.get("Chiều") else "Trống",
                            "10h30": ", ".join(shifts.get("10h30", [])) if shifts.get("10h30") else "Trống"
                        })
                    st.dataframe(pd.DataFrame(lich_list), hide_index=True, use_container_width=True)

        # ==========================================
        # TAB 3: QUỸ SHOP
        # ==========================================
        if "💰 QUỸ SHOP" in allowed_tabs:
            with tabs[allowed_tabs.index("💰 QUỸ SHOP")]:
                st.markdown("### 💰 Sổ Quỹ Cửa Hàng")
                qs = db.get("quy_shop", {})
                tong_thu = sum(float(i.get("amount", 0)) for i in qs.values() if i.get("type") == "Thu")
                tong_chi = sum(float(i.get("amount", 0)) for i in qs.values() if i.get("type") == "Chi")
                ton_quy = tong_thu - tong_chi
                
                c1, c2, c3 = st.columns(3)
                c1.metric("TỒN QUỸ", format_vnd(ton_quy))
                c2.metric("Tổng Thu", format_vnd(tong_thu))
                c3.metric("Tổng Chi", format_vnd(tong_chi))
                st.divider()
                
                if st.session_state.is_admin:
                    with st.expander("➕ THÊM GIAO DỊCH", expanded=False):
                        with st.form("fund_form", clear_on_submit=True):
                            f_type = st.selectbox("Loại", ["Thu", "Chi"])
                            f_amt = st.number_input("Số tiền", min_value=0, step=50000)
                            f_desc = st.text_input("Chi tiết / Lý do")
                            if st.form_submit_button("LƯU VÀO SỔ", type="primary", use_container_width=True):
                                if f_amt > 0 and f_desc:
                                    tx_id = str(int(time.time() * 1000))
                                    now_str = (datetime.utcnow() + timedelta(hours=7)).strftime("%d/%m/%Y %H:%M")
                                    update_firebase("quy_shop", {tx_id: {"date": now_str, "type": f_type, "amount": f_amt, "desc": f_desc, "user": st.session_state.user}})
                                    st.success("✅ Đã lưu!"); time.sleep(0.5); st.rerun()
                                else: st.error("❌ Nhập đủ số tiền và lý do!")
                
                st.markdown("#### 📜 Lịch Sử Thu Chi")
                if not qs: st.caption("Sổ quỹ trống.")
                else:
                    quy_list = []
                    for tx_id, tx in sorted(qs.items(), key=lambda x: x[0], reverse=True):
                        quy_list.append({
                            "Mã": f"...{tx_id[-5:]}",
                            "Ngày": tx.get("date", ""),
                            "Loại": "➕ Thu" if tx.get("type") == "Thu" else "➖ Chi",
                            "Số Tiền": f"{float(tx.get('amount', 0)):,.0f} đ".replace(",", "."),
                            "Lý do": tx.get("desc", ""),
                            "Người nhập": tx.get("user", "")
                        })
                    st.dataframe(pd.DataFrame(quy_list), hide_index=True, use_container_width=True)
                    
                    if st.session_state.is_admin:
                        st.caption("Xóa giao dịch (Nếu nhập nhầm):")
                        xoa_id = st.selectbox("Chọn Mã cần xóa:", [tx["Mã"] for tx in quy_list])
                        if st.button("Xóa giao dịch này"):
                            full_id = [tid for tid in qs.keys() if tid[-5:] == xoa_id[-5:]][0]
                            delete_firebase(f"quy_shop/{full_id}")
                            st.success("Đã xóa!"); time.sleep(0.5); st.rerun()

        # ==========================================
        # TAB 4: PHÂN QUYỀN (CHỈ ADMIN THẤY)
        # ==========================================
        if "👥 QUẢN LÝ TÀI KHOẢN" in allowed_tabs:
            with tabs[allowed_tabs.index("👥 QUẢN LÝ TÀI KHOẢN")]:
                st.markdown("### ⏳ Yêu Cầu Đăng Ký Mới")
                pending = db.get("pending_users", {})
                if not pending: st.info("Không có yêu cầu chờ.")
                else:
                    for pu, pinfo in pending.items():
                        c1, c2, c3 = st.columns([2, 1, 1])
                        c1.markdown(f"Tài khoản: **{pu}**")
                        if c2.button("✅ Duyệt", key=f"ok_{pu}", use_container_width=True):
                            update_firebase(f"users/{pu}", {"pass": pinfo["pass"], "role": "user", "permissions": ["XEM LỊCH", "TÍCH LŨY"]})
                            delete_firebase(f"pending_users/{pu}")
                            st.rerun()
                        if c3.button("❌ Bỏ", key=f"rej_{pu}", use_container_width=True):
                            delete_firebase(f"pending_users/{pu}")
                            st.rerun()
                
                st.divider()
                st.markdown("### ⚙️ Phân Quyền Nhân Viên")
                users = db.get("users", {})
                for u, uinfo in users.items():
                    if uinfo.get("role") != "admin":
                        with st.expander(f"👤 {u}"):
                            current_perms = uinfo.get("permissions", [])
                            new_perms = st.multiselect("Được xem các bảng:", 
                                ["TÍCH LŨY", "XEM LỊCH", "QUỸ SHOP"], 
                                default=[p for p in current_perms if p in ["TÍCH LŨY", "XEM LỊCH", "QUỸ SHOP"]],
                                key=f"perm_{u}"
                            )
                            if st.button("💾 Lưu Quyền", key=f"save_{u}"):
                                update_firebase(f"users/{u}/permissions", new_perms)
                                st.success(f"Đã lưu!"); time.sleep(0.5); st.rerun()
