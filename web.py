import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime, timedelta

# ==========================================
# CẤU HÌNH GIAO DIỆN & TÀNG HÌNH NÚT THỪA
# ==========================================
st.set_page_config(page_title="HTCV System", page_icon="⚡", layout="wide")

# BÙA CHÚ CSS MẠNH NHẤT ĐỂ DIỆT 2 ICON TRÊN MOBILE VÀ NÚT MANAGE
custom_css = """
<style>
    /* Giấu menu, header, footer mặc định */
    header {visibility: hidden !important; display: none !important;}
    footer {visibility: hidden !important; display: none !important;}
    
    /* Ẩn các nút nổi (Floating buttons) trên Mobile và PC */
    [data-testid="stToolbar"] {visibility: hidden !important; display: none !important;}
    [data-testid="stDecoration"] {visibility: hidden !important; display: none !important;}
    [data-testid="manage-app-button"] {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    
    /* Ẩn cục diện Manage App, Viewer Badge của Streamlit Cloud */
    .viewerBadge_container {display: none !important;}
    .viewerBadge_link {display: none !important;}
    #viewerBadge_container_0 {display: none !important;}
    .stDeployButton {display: none !important;}
    
    /* Chặn triệt để mọi iframe/badge quảng cáo nổi ở góc phải dưới */
    iframe[title="streamlit_cloud_badges"] {display: none !important;}
    div[class^="st-emotion-cache-"] > iframe {display: none !important;}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# KẾT NỐI CƠ SỞ DỮ LIỆU FIREBASE
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

# Khởi tạo session (biến nhớ)
if "user" not in st.session_state:
    st.session_state.user = None
    st.session_state.is_admin = False
    st.session_state.page = "login"
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

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
    
    # --- THANH BÊN (SIDEBAR) ---
    with st.sidebar:
        st.markdown(f"<h2 style='color:#0ea5e9; text-align:center;'>HTCV SYSTEM</h2>", unsafe_allow_html=True)
        if st.session_state.is_admin: st.success("👑 QUYỀN ADMIN")
        else: st.info("👤 QUYỀN NHÂN VIÊN")
            
        st.markdown(f"**Xin chào, {st.session_state.user.upper()}**")
        st.divider()

        # NÚT ĐỔI MÀU SÁNG / TỐI
        theme_icon = "🌞 Giao diện Sáng" if st.session_state.theme == "Dark" else "🌙 Giao diện Tối"
        if st.button(theme_icon, use_container_width=True):
            st.session_state.theme = "Light" if st.session_state.theme == "Dark" else "Dark"
            st.rerun()

        with st.expander("🔑 Đổi mật khẩu cá nhân"):
            old_p = st.text_input("Mật khẩu cũ", type="password")
            new_p = st.text_input("Mật khẩu mới", type="password")
            if st.button("Xác nhận đổi", use_container_width=True):
                if old_p == u_info.get("pass"):
                    update_firebase(f"users/{st.session_state.user}", {"pass": new_p, "role": u_info.get("role"), "permissions": perms})
                    st.success("Đã đổi pass!")
                else: st.error("Sai mật khẩu cũ!")

        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚪 ĐĂNG XUẤT", type="primary", use_container_width=True):
            st.session_state.user = None
            st.session_state.is_admin = False
            st.rerun()

    # --- LỌC TABS DỰA TRÊN QUYỀN ---
    tab_dict = {"🎯 KPI": "TÍCH LŨY", "🗓️ LỊCH TRỰC": "XEM LỊCH", "💰 QUỸ SHOP": "QUỸ SHOP"}
    allowed_tabs = []
    
    if st.session_state.is_admin: 
        allowed_tabs = list(tab_dict.keys()) + ["👥 QUẢN LÝ TÀI KHOẢN"]
    else: 
        allowed_tabs = [k for k, v in tab_dict.items() if v in perms]

    if not allowed_tabs:
        st.error("Tài khoản của bạn chưa được cấp quyền truy cập tính năng nào. Báo Admin!")
    else:
        tabs = st.tabs(allowed_tabs)
        
        # ==========================================
        # TAB 1: BẢNG KPI
        # ==========================================
        if "🎯 KPI" in allowed_tabs:
            with tabs[allowed_tabs.index("🎯 KPI")]:
                st.markdown("### 🎯 Tiến Độ KPI Tháng Này")
                kpi_data = db.get("kpi", {}).get("emp", {})
                
                if not kpi_data: st.info("Chưa có dữ liệu KPI tháng này.")
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
                        st.caption("💡 Lời khuyên cho Admin: Bạn có thể click đúp chuột thẳng vào cột 'Đã Bán' ở bảng dưới đây để sửa số lượng, sau đó bấm nút Lưu.")
                        edited_df = st.data_editor(df_kpi, hide_index=True, disabled=["Nhân Viên", "Target", "Còn Thiếu"], use_container_width=True)
                        
                        if st.button("💾 LƯU BẢNG KPI", type="primary"):
                            for idx, row in edited_df.iterrows():
                                emp = row["Nhân Viên"]
                                new_sold = int(row["Đã Bán"])
                                update_firebase(f"kpi/emp/{emp}", {"sold": new_sold})
                            st.success("Đã đồng bộ lên Đám mây thành công!"); time.sleep(0.5); st.rerun()
                    else:
                        st.dataframe(df_kpi, hide_index=True, use_container_width=True)

        # ==========================================
        # TAB 2: GIAO DIỆN BẢNG LỊCH TRỰC
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
                            "Ngày Trực": date_str,
                            "Ca Sáng": ", ".join(shifts.get("Sáng", [])) if shifts.get("Sáng") else "Trống",
                            "Ca Chiều": ", ".join(shifts.get("Chiều", [])) if shifts.get("Chiều") else "Trống",
                            "Ca 10h30": ", ".join(shifts.get("10h30", [])) if shifts.get("10h30") else "Trống"
                        })
                    df_lich = pd.DataFrame(lich_list)
                    st.dataframe(df_lich, hide_index=True, use_container_width=True)

        # ==========================================
        # TAB 3: BẢNG QUỸ SHOP
        # ==========================================
        if "💰 QUỸ SHOP" in allowed_tabs:
            with tabs[allowed_tabs.index("💰 QUỸ SHOP")]:
                st.markdown("### 💰 Sổ Quỹ Cửa Hàng")
                qs = db.get("quy_shop", {})
                
                tong_thu = sum(float(i.get("amount", 0)) for i in qs.values() if i.get("type") == "Thu")
                tong_chi = sum(float(i.get("amount", 0)) for i in qs.values() if i.get("type") == "Chi")
                ton_quy = tong_thu - tong_chi
                
                c1, c2, c3 = st.columns(3)
                c1.metric("TỒN QUỸ", f"{ton_quy:,.0f} đ".replace(",", "."))
                c2.metric("Tổng Thu", f"{tong_thu:,.0f} đ".replace(",", "."))
                c3.metric("Tổng Chi", f"{tong_chi:,.0f} đ".replace(",", "."))
                st.divider()
                
                if st.session_state.is_admin:
                    with st.expander("➕ THÊM GIAO DỊCH", expanded=False):
                        with st.form("fund_form", clear_on_submit=True):
                            c_t, c_a = st.columns([1, 2])
                            f_type = c_t.selectbox("Loại Giao Dịch", ["Thu", "Chi"])
                            f_amt = c_a.number_input("Số tiền (VNĐ)", min_value=0, step=50000)
                            f_desc = st.text_input("Chi tiết / Lý do (Vd: Bán hàng, Tiền điện...)")
                            
                            if st.form_submit_button("LƯU VÀO SỔ", type="primary", use_container_width=True):
                                if f_amt > 0 and f_desc:
                                    tx_id = str(int(time.time() * 1000))
                                    now_str = (datetime.utcnow() + timedelta(hours=7)).strftime("%d/%m/%Y %H:%M")
                                    update_firebase("quy_shop", {tx_id: {"date": now_str, "type": f_type, "amount": f_amt, "desc": f_desc, "user": st.session_state.user}})
                                    st.success("✅ Đã lưu vào sổ quỹ!"); time.sleep(0.5); st.rerun()
                                else: st.error("❌ Vui lòng nhập số tiền và chi tiết!")
                
                st.markdown("#### 📜 Lịch Sử Giao Dịch")
                if not qs: st.caption("Sổ quỹ đang trống.")
                else:
                    quy_list = []
                    for tx_id, tx in sorted(qs.items(), key=lambda x: x[0], reverse=True):
                        quy_list.append({
                            "Mã Lệnh": f"...{tx_id[-5:]}",
                            "Ngày Giờ": tx.get("date", ""),
                            "Loại": "➕ Thu" if tx.get("type") == "Thu" else "➖ Chi",
                            "Số Tiền": f"{float(tx.get('amount', 0)):,.0f} đ".replace(",", "."),
                            "Lý do": tx.get("desc", ""),
                            "Người nhập": tx.get("user", "")
                        })
                    
                    df_quy = pd.DataFrame(quy_list)
                    st.dataframe(df_quy, hide_index=True, use_container_width=True)
                    
                    if st.session_state.is_admin:
                        st.caption("Xóa giao dịch (Nếu nhập nhầm):")
                        xoa_id = st.selectbox("Chọn Mã Lệnh cần xóa:", [tx["Mã Lệnh"] for tx in quy_list])
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
                if not pending: st.info("Không có yêu cầu chờ duyệt.")
                else:
                    for pu, pinfo in pending.items():
                        c1, c2, c3 = st.columns([2, 1, 1])
                        c1.markdown(f"Tài khoản: **{pu}**")
                        if c2.button("✅ Duyệt", key=f"ok_{pu}", use_container_width=True):
                            update_firebase(f"users/{pu}", {"pass": pinfo["pass"], "role": "user", "permissions": ["XEM LỊCH", "TÍCH LŨY"]})
                            delete_firebase(f"pending_users/{pu}")
                            st.success("Đã duyệt!"); time.sleep(0.5); st.rerun()
                        if c3.button("❌ Từ chối", key=f"rej_{pu}", use_container_width=True):
                            delete_firebase(f"pending_users/{pu}")
                            st.rerun()
                
                st.divider()
                
                st.markdown("### ⚙️ Phân Quyền Nhân Viên")
                users = db.get("users", {})
                for u, uinfo in users.items():
                    if uinfo.get("role") != "admin":
                        with st.expander(f"👤 Nhân viên: {u}"):
                            current_perms = uinfo.get("permissions", [])
                            new_perms = st.multiselect("Chức năng được phép xem trên Web:", 
                                ["TÍCH LŨY", "XEM LỊCH", "QUỸ SHOP"], 
                                default=[p for p in current_perms if p in ["TÍCH LŨY", "XEM LỊCH", "QUỸ SHOP"]],
                                key=f"perm_{u}"
                            )
                            if st.button("💾 Lưu Quyền", key=f"save_{u}"):
                                update_firebase(f"users/{u}/permissions", new_perms)
                                st.success(f"Đã cập nhật quyền thành công!"); time.sleep(0.5); st.rerun()
