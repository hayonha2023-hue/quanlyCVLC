import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
import time
import hashlib
import io
import base64
from PIL import Image, ImageOps
from datetime import datetime, timedelta

# ==========================================
# CẤU HÌNH GIAO DIỆN & SIÊU HIỆU ỨNG CSS
# ==========================================
st.set_page_config(page_title="HTCV by DatTT System", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

base_css = """
<style>
    @keyframes SAFadeInUp {
        0% { opacity: 0; transform: translateY(12px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    [data-testid="stMainBlockContainer"] { animation: SAFadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
    header { background-color: transparent !important; }
    [data-testid="stHeaderActionElements"], .stDeployButton, #manage-app-button, footer {display: none !important;}
    
    [data-testid="stForm"] { border-radius: 20px !important; border: 1px solid rgba(150, 150, 150, 0.2) !important; padding: 40px !important; background: rgba(150, 150, 150, 0.03) !important; box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1) !important; }
    [data-testid="stTextInput"] label p { font-size: 14px !important; font-weight: 800 !important; color: #0ea5e9 !important; letter-spacing: 1px !important; margin-bottom: 8px !important; }
    div[data-baseweb="input"] { border-radius: 12px !important; border: 2px solid rgba(150, 150, 150, 0.2) !important; background-color: transparent !important; }
    div[data-baseweb="input"]:focus-within { border-color: #0ea5e9 !important; box-shadow: 0 0 10px rgba(14, 165, 233, 0.2) !important; background-color: rgba(14, 165, 233, 0.05) !important; }
    div[data-baseweb="input"] input { padding: 16px 15px !important; font-size: 16px !important; font-weight: 600 !important; }

    .stButton>button { border-radius: 12px !important; font-weight: 700 !important; height: 48px !important; transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important; }
    .stButton>button:hover { transform: translateY(-2px) !important; box-shadow: 0 6px 15px rgba(14, 165, 233, 0.3) !important; }
    
    [data-testid="stMetric"] { border-radius: 18px !important; padding: 20px !important; border: 1px solid rgba(14, 165, 233, 0.15) !important; }
    [data-testid="stMetric"]:hover { transform: translateY(-4px) !important; border-color: #0ea5e9 !important; box-shadow: 0 12px 24px rgba(14, 165, 233, 0.15) !important; }
    [data-testid="stMetricValue"] { font-size: 2.2rem !important; font-weight: 800 !important; }
    [data-testid="stExpander"] { border-radius: 14px !important; overflow: hidden !important; border: 1px solid rgba(150, 150, 150, 0.12) !important; }

    [data-testid="stSidebar"] div[role="radiogroup"] > label { background-color: transparent !important; border-radius: 12px !important; padding: 14px 18px !important; margin-bottom: 10px !important; cursor: pointer; transition: all 0.2s !important; }
    [data-testid="stSidebar"] div[role="radiogroup"] > label:hover { background-color: rgba(14, 165, 233, 0.08) !important; }
    [data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] { background-color: rgba(14, 165, 233, 0.15) !important; border-left: 5px solid #0ea5e9 !important; }
    [data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child { display: none !important; }
    [data-testid="stSidebar"] div[role="radiogroup"] > label p { font-size: 16px !important; font-weight: 600 !important; }
</style>
"""
st.markdown(base_css, unsafe_allow_html=True)

FIREBASE_URL = "https://htcv-5c857-default-rtdb.firebaseio.com/htcv.json"

def get_data():
    try:
        r = requests.get(FIREBASE_URL)
        return r.json() if r.status_code == 200 else {}
    except: return {}

def update_firebase(path, data): requests.patch(f"{FIREBASE_URL.replace('.json', '')}/{path}.json", json=data)
def delete_firebase(path): requests.delete(f"{FIREBASE_URL.replace('.json', '')}/{path}.json")
def format_vnd(amount): return f"{amount:,.0f} ₫".replace(",", ".")
def get_hash(text): return hashlib.md5(text.encode('utf-8')).hexdigest()

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
    theme_css = """<style>[data-testid="stAppViewContainer"] {background-color: #f1f5f9 !important;} [data-testid="stSidebar"] {background-color: #ffffff !important;} .stApp {background-color: #f1f5f9 !important; color: #0f172a !important;} .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, label, span, th, td {color: #1e293b !important;} [data-testid="stMetricValue"] {color: #0284c7 !important;} [data-testid="stMetric"], [data-testid="stForm"], [data-testid="stExpander"] {background-color: #ffffff !important;} button[kind="secondary"] { background-color: #ffffff !important; color: #0284c7 !important; border: 1px solid #e2e8f0 !important; } button[kind="secondary"]:hover { background-color: #f0f9ff !important; border-color: #0ea5e9 !important; }</style>"""
else:
    theme_css = """<style>[data-testid="stAppViewContainer"] {background-color: #090d16 !important;} [data-testid="stSidebar"] {background-color: #111827 !important;} .stApp {background-color: #090d16 !important; color: #f8fafc !important;} .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, label, span, th, td {color: #f1f5f9 !important;} [data-testid="stMetricValue"] {color: #38bdf8 !important;} [data-testid="stMetric"], [data-testid="stForm"], [data-testid="stExpander"] {background-color: #1f2937 !important;} button[kind="secondary"] { background-color: #1f2937 !important; color: #38bdf8 !important; border: 1px solid #374151 !important; } button[kind="secondary"]:hover { background-color: #111827 !important; border-color: #38bdf8 !important; }</style>"""
st.markdown(theme_css, unsafe_allow_html=True)

# Tự động duy trì phiên đăng nhập bằng query_params
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
    _, col_center, _ = st.columns([1, 1.8, 1])
    with col_center:
        st.markdown("<br>", unsafe_allow_html=True)
        import os, base64
        logo_html = ""
        img_path = "Logo.png" if os.path.exists("Logo.png") else ("Logo.ico" if os.path.exists("Logo.ico") else "")
        if img_path:
            with open(img_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
                logo_html = f"<img src='data:image/png;base64,{b64}' style='width: 100px; height: 100px; border-radius: 24px; box-shadow: 0 10px 30px rgba(14, 165, 233, 0.4); margin-bottom: 15px; border: 1px solid rgba(14,165,233,0.3);'>"
        else:
            logo_html = """
            <div style='display: inline-flex; align-items: center; justify-content: center; width: 85px; height: 85px; border-radius: 50%; background: rgba(14, 165, 233, 0.05); border: 2px solid rgba(14, 165, 233, 0.4); box-shadow: 0 0 25px rgba(14, 165, 233, 0.15); margin-bottom: 15px;'>
                <svg width="38" height="38" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><rect x="9" y="10" width="6" height="6" rx="1" ry="1"></rect><path d="M12 10v-2a2 2 0 1 1 4 0v2"></path></svg>
            </div>"""

        st.markdown(f"<div style='text-align: center; margin-bottom: 25px;'>{logo_html}<h1 style='color: #0ea5e9; font-size: 2.5rem; font-weight:900; margin: 0; letter-spacing: 1.5px;'>HTCV by DatTT</h1></div>", unsafe_allow_html=True)
        
        if st.session_state.page == "login":
            with st.form("login_form"):
                st.markdown("<h4 style='text-align: center; margin-bottom: 30px; font-weight:800; color: #64748b;'>XÁC THỰC TÀI KHOẢN</h4>", unsafe_allow_html=True)
                u = st.text_input("👤 TÀI KHOẢN TRUY CẬP").strip().lower()
                p = st.text_input("🔑 MẬT KHẨU BẢO MẬT", type="password")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("🚀 ĐĂNG NHẬP", type="primary", use_container_width=True):
                    users = db.get("users", {})
                    if u in users and users[u]["pass"] == p:
                        st.session_state.user = u
                        st.session_state.is_admin = (users[u].get("role") == "admin")
                        st.query_params["u"] = u
                        st.query_params["t"] = get_hash(p)
                        st.rerun()
                    elif u in db.get("pending_users", {}): st.warning("⏳ Tài khoản đang chờ duyệt!")
                    else: st.error("❌ Sai thông tin đăng nhập!")
                    
            c1, c2 = st.columns(2)
            if c1.button("📝 Đăng ký tài khoản", use_container_width=True): st.session_state.page = "register"; st.rerun()
            if c2.button("❓ Quên mật khẩu", use_container_width=True): st.session_state.page = "forgot"; st.rerun()

        elif st.session_state.page == "register":
            with st.form("reg_form"):
                st.markdown("<h4 style='text-align: center; margin-bottom: 30px; font-weight:800; color: #64748b;'>ĐĂNG KÝ MỚI</h4>", unsafe_allow_html=True)
                new_u = st.text_input("Tên đăng nhập").strip().lower()
                new_p = st.text_input("Mật khẩu truy cập", type="password")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("GỬI YÊU CẦU DUYỆT", type="primary", use_container_width=True):
                    if new_u and new_p:
                        update_firebase("pending_users", {new_u: {"pass": new_p}})
                        st.success("✅ Đã gửi! Vui lòng báo Admin duyệt.")
                    else: st.error("Nhập đủ thông tin!")
            if st.button("⬅ Quay lại", use_container_width=True): st.session_state.page = "login"; st.rerun()

        elif st.session_state.page == "forgot":
            with st.form("forgot_form"):
                st.markdown("<h4 style='text-align: center; margin-bottom: 30px; font-weight:800; color: #64748b;'>KHÔI PHỤC MẬT KHẨU</h4>", unsafe_allow_html=True)
                u = st.text_input("Tài khoản cần khôi phục").strip().lower()
                new_p = st.text_input("Mật khẩu mới", type="password")
                secret = st.text_input("Mã xác thực Admin", type="password")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("XÁC NHẬN", type="primary", use_container_width=True):
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
    edit_perms = u_info.get("edit_permissions", []) 
    
    tab_dict = {"🎯 BẢNG KPI": "TÍCH LŨY", "🗓️ LỊCH TRỰC": "XEM LỊCH", "📊 CHIA TARGET": "TARGET KPI", "🛒 LỊCH ECOM": "LỊCH ECOM", "📍 THI TRƯỜNG": "THỊ TRƯỜNG", "💰 SỔ QUỸ SHOP": "QUỸ SHOP", "🤖 AI TƯ VẤN": "AI TƯ VẤN"}
    allowed_tabs = []
    
    hidden = db.get("settings", {}).get("hidden_features", [])

    if st.session_state.is_admin: 
        allowed_tabs = [k for k, v in tab_dict.items() if v not in hidden] + ["👥 QUẢN TRỊ ADMIN"]
    else: 
        allowed_tabs = [k for k, v in tab_dict.items() if (v in perms) and (v not in hidden)]

    if not allowed_tabs:
        st.error("Tài khoản chưa được cấp quyền truy cập hoặc chức năng đang bị ẩn.")
        if st.button("Thoát"): logout()
    else:
        with st.sidebar:
            role_icon = "👑" if st.session_state.is_admin else "👤"
            st.markdown(f"<h2 style='text-align: center; color: #0ea5e9; font-weight:800;'>{role_icon} {st.session_state.user.upper()}</h2>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; color: #64748b; font-size: 13px;'>{ 'BAN QUẢN TRỊ SYSTEM' if st.session_state.is_admin else 'NHÂN VIÊN CƠ SỞ' }</p>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            selected_tab = st.radio("MENU CHỨC NĂNG", allowed_tabs, label_visibility="collapsed")
            st.markdown("<br><hr style='border-color: rgba(150,150,150,0.1);'><br>", unsafe_allow_html=True)
            
            if st.button("🔑 Cài đặt mật khẩu", use_container_width=True):
                st.session_state.show_pass = not st.session_state.get("show_pass", False)
                st.session_state.force_close_sidebar = True
                
            theme_txt = "☀️ Giao diện Sáng" if st.session_state.theme == "Dark" else "🌙 Giao diện Tối"
            if st.button(theme_txt, use_container_width=True):
                st.session_state.theme = "Light" if st.session_state.theme == "Dark" else "Dark"
                st.session_state.force_close_sidebar = True
                
            if st.button("🚪 Đăng xuất", use_container_width=True): logout()

        # Logic tự thu gọn thanh Menu
        if "last_tab" not in st.session_state: st.session_state.last_tab = selected_tab
        need_close = False
        if st.session_state.last_tab != selected_tab:
            st.session_state.last_tab = selected_tab
            need_close = True
        if st.session_state.get("force_close_sidebar", False):
            need_close = True
            st.session_state.force_close_sidebar = False
            
        if need_close:
            components.html('''<script>var doc = window.parent.document; var desktopBtn = doc.querySelector('[data-testid="stSidebarCollapseButton"] button'); if (desktopBtn) { desktopBtn.click(); } var mobileBtns = doc.querySelectorAll('button[aria-label="Close"], button[aria-label="Collapse sidebar"], button[title="Collapse sidebar"]'); mobileBtns.forEach(function(btn) { btn.click(); });</script>''', height=0, width=0)

        # XỬ LÝ ĐỔI PASS
        if st.session_state.get("show_pass", False):
            with st.container():
                st.markdown("<div style='padding: 22px; border-radius: 16px; background-color: rgba(14, 165, 233, 0.04); border: 1px solid rgba(14, 165, 233, 0.2); margin-bottom: 25px;'>", unsafe_allow_html=True)
                cc1, cc2, cc3 = st.columns([3, 3, 2])
                old_p = cc1.text_input("Mật khẩu cũ", type="password")
                new_p = cc2.text_input("Mật khẩu mới", type="password")
                cc3.markdown("<div style='padding-top: 28px;'></div>", unsafe_allow_html=True)
                if cc3.button("💾 CẬP NHẬT", type="primary", use_container_width=True):
                    if old_p == u_info.get("pass"):
                        update_firebase(f"users/{st.session_state.user}", {"pass": new_p, "role": u_info.get("role"), "permissions": perms, "edit_permissions": edit_perms})
                        st.query_params["t"] = get_hash(new_p)
                        st.success("Thành công!")
                        st.session_state.show_pass = False; time.sleep(1); st.rerun()
                    else: cc3.error("Sai pass cũ!")
                st.markdown("</div>", unsafe_allow_html=True)

        # ==========================================
        # 1. TAB BẢNG KPI
        # ==========================================
        if selected_tab == "🎯 BẢNG KPI":
            st.markdown("<h3 style='margin-top: 0px; margin-bottom: 25px; font-weight:800;'>🎯 Tiến Độ Hoàn Thành KPI Tháng Này</h3>", unsafe_allow_html=True)
            kpi_imgs = db.get("kpi_images", [])
            if not isinstance(kpi_imgs, list): kpi_imgs = []
            
            if st.session_state.is_admin or "SỬA SỐ KPI" in edit_perms:
                with st.expander("📸 QUẢN LÝ ẢNH DANH MỤC KPI"):
                    uploaded_files = st.file_uploader("Chọn nhiều ảnh Bảng tính KPI", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="kpi_up")
                    if 'rot_angles_kpi' not in st.session_state: st.session_state.rot_angles_kpi = {}
                    if uploaded_files:
                        for i, up_file in enumerate(uploaded_files):
                            fname = up_file.name
                            if fname not in st.session_state.rot_angles_kpi: st.session_state.rot_angles_kpi[fname] = 0
                            preview_img = Image.open(up_file)
                            preview_img = ImageOps.exif_transpose(preview_img)
                            angle = st.session_state.rot_angles_kpi[fname]
                            if angle != 0: preview_img = preview_img.rotate(angle, expand=True)
                            st.image(preview_img, use_container_width=True)
                            if st.button(f"🔄 Xoay riêng ảnh {i+1} 90 độ", key=f"rot_kpi_{i}_{fname}", use_container_width=True):
                                st.session_state.rot_angles_kpi[fname] = (st.session_state.rot_angles_kpi[fname] - 90) % 360
                                st.rerun()
                            
                        if st.button("💾 LƯU BỘ ẢNH NÀY", type="primary", use_container_width=True, key="kpi_save"):
                            new_img_list = []
                            for up_file in uploaded_files:
                                fname = up_file.name
                                img = Image.open(up_file)
                                img = ImageOps.exif_transpose(img)
                                angle = st.session_state.rot_angles_kpi.get(fname, 0)
                                if angle != 0: img = img.rotate(angle, expand=True)
                                img.thumbnail((1600, 1600)) 
                                buffered = io.BytesIO()
                                img.convert("RGB").save(buffered, format="JPEG", quality=85)
                                new_img_list.append(base64.b64encode(buffered.getvalue()).decode())
                            update_firebase("kpi_images", new_img_list)
                            st.session_state.rot_angles_kpi = {} 
                            st.success(f"Đã lưu ảnh!"); time.sleep(1); st.rerun()
                            
                    if kpi_imgs:
                        if st.button("🗑️ Xóa TOÀN BỘ ảnh", type="primary", key="kpi_del"):
                            delete_firebase("kpi_images"); st.rerun()

            if kpi_imgs:
                with st.expander(f"📄 MỞ XEM BẢNG DANH MỤC KPI ({len(kpi_imgs)} trang)", expanded=False):
                    for idx, img_b64 in enumerate(kpi_imgs):
                        try: st.image(base64.b64decode(img_b64), use_container_width=True)
                        except: st.error(f"Lỗi ảnh {idx + 1}")
            
            st.markdown("<hr style='border-color: rgba(150,150,150,0.1); margin-top: 10px; margin-bottom: 20px;'>", unsafe_allow_html=True)
            kpi_node = db.get("kpi", {})
            kpi_data = kpi_node.get("emp", {})
            if isinstance(kpi_data, list): kpi_data = {str(i): v for i, v in enumerate(kpi_data) if v is not None}
            
            if not kpi_data: st.info("Chưa có dữ liệu KPI.")
            else:
                tot_t = int(kpi_node.get("tot", 0))
                tot_s = sum(int(d.get("sold", 0)) for d in kpi_data.values() if isinstance(d, dict))
                pct = (tot_s / tot_t * 100) if tot_t > 0 else 0
                c1, c2, c3 = st.columns(3)
                c1.metric("MỤC TIÊU", f"{tot_t:,}".replace(",", "."))
                c2.metric("ĐÃ BÁN", f"{tot_s:,}".replace(",", "."))
                c3.metric("TIẾN ĐỘ", f"{pct:.1f}%")

                kpi_list = []
                for emp, info in kpi_data.items():
                    tgt = info.get("tgt", 0); sold = info.get("sold", 0); rem = max(0, tgt - sold)
                    kpi_list.append({"Nhân Viên": emp, "Đã Bán (Số lượng)": sold, "Target Giao": tgt, "Còn Thiếu KPI": rem})
                df_kpi = pd.DataFrame(kpi_list)

                if st.session_state.is_admin or "SỬA SỐ KPI" in edit_perms:
                    edited_df = st.data_editor(df_kpi, hide_index=True, disabled=["Nhân Viên", "Target Giao", "Còn Thiếu KPI"], use_container_width=True)
                    if st.button("💾 LƯU SỐ LIỆU", type="primary", use_container_width=True):
                        for idx, row in edited_df.iterrows(): update_firebase(f"kpi/emp/{row['Nhân Viên']}", {"sold": int(row["Đã Bán (Số lượng)"])})
                        st.success("Đã đồng bộ!"); time.sleep(0.5); st.rerun()
                else: st.dataframe(df_kpi, hide_index=True, use_container_width=True)

        # ==========================================
        # 2. TAB LỊCH TRỰC
        # ==========================================
        elif selected_tab == "🗓️ LỊCH TRỰC":
            st.markdown("<h3 style='margin-top: 0px; margin-bottom: 25px; font-weight:800;'>🗓️ Bảng Phân Phối Lịch Trực Tuần</h3>", unsafe_allow_html=True)
            sched_imgs = db.get("schedule_images", [])
            if not isinstance(sched_imgs, list): sched_imgs = []
            
            if st.session_state.is_admin or "UP ẢNH LỊCH TRỰC" in edit_perms:
                with st.expander("📸 QUẢN LÝ ẢNH BẢNG LỊCH TRỰC"):
                    uploaded_files = st.file_uploader("Chọn ảnh Lịch trực", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="sched_up")
                    if 'rot_angles_sched' not in st.session_state: st.session_state.rot_angles_sched = {}
                    if uploaded_files:
                        for i, up_file in enumerate(uploaded_files):
                            fname = up_file.name
                            if fname not in st.session_state.rot_angles_sched: st.session_state.rot_angles_sched[fname] = 0
                            preview_img = Image.open(up_file)
                            preview_img = ImageOps.exif_transpose(preview_img)
                            angle = st.session_state.rot_angles_sched[fname]
                            if angle != 0: preview_img = preview_img.rotate(angle, expand=True)
                            st.image(preview_img, use_container_width=True)
                            if st.button(f"🔄 Xoay riêng ảnh {i+1}", key=f"rot_sched_{i}_{fname}", use_container_width=True):
                                st.session_state.rot_angles_sched[fname] = (st.session_state.rot_angles_sched[fname] - 90) % 360
                                st.rerun()
                                
                        if st.button("💾 LƯU LỊCH NÀY", type="primary", use_container_width=True, key="sched_save"):
                            new_img_list = []
                            for up_file in uploaded_files:
                                fname = up_file.name
                                img = Image.open(up_file)
                                img = ImageOps.exif_transpose(img)
                                angle = st.session_state.rot_angles_sched.get(fname, 0)
                                if angle != 0: img = img.rotate(angle, expand=True)
                                img.thumbnail((1600, 1600)) 
                                buffered = io.BytesIO()
                                img.convert("RGB").save(buffered, format="JPEG", quality=85)
                                new_img_list.append(base64.b64encode(buffered.getvalue()).decode())
                            update_firebase("schedule_images", new_img_list)
                            st.session_state.rot_angles_sched = {}
                            st.success(f"Đã tải ảnh lên!"); time.sleep(1); st.rerun()
                            
                    if sched_imgs:
                        if st.button("🗑️ Xóa TOÀN BỘ lịch", type="primary", key="sched_del"):
                            delete_firebase("schedule_images"); st.rerun()

            if sched_imgs:
                with st.expander(f"📄 MỞ XEM BỘ ẢNH LỊCH TRỰC ({len(sched_imgs)} trang)", expanded=False):
                    for idx, img_b64 in enumerate(sched_imgs):
                        try: st.image(base64.b64decode(img_b64), use_container_width=True)
                        except: st.error(f"Lỗi ảnh {idx + 1}")
            
            st.markdown("<hr style='border-color: rgba(150,150,150,0.1); margin-top: 10px; margin-bottom: 20px;'>", unsafe_allow_html=True)
            history = db.get("detailed_history", {})
            if not history: st.info("Chưa có thông tin lịch chia tự động.")
            else:
                hidden = db.get("settings", {}).get("hidden_features", [])
                lich_list = []
                for date_str, shifts in history.items():
                    row_data = {
                        "Mốc Thời Gian": date_str,
                        "Ca Sáng": ", ".join(shifts.get("Sáng", [])) if shifts.get("Sáng") else "-",
                        "Ca Chiều": ", ".join(shifts.get("Chiều", [])) if shifts.get("Chiều") else "-"
                    }
                    if "CA 10H30" not in hidden: row_data["Ca Đêm (10h30)"] = ", ".join(shifts.get("10h30", [])) if shifts.get("10h30") else "-"
                    lich_list.append(row_data)
                st.dataframe(pd.DataFrame(lich_list), hide_index=True, use_container_width=True)
        # ==========================================
        # 2.5 TAB CHIA TARGET (ĐỒNG BỘ 2 CHIỀU VỚI APP PC)
        # ==========================================
        elif selected_tab == "📊 CHIA TARGET":
            st.markdown("<h3 style='margin-top: 0px; margin-bottom: 25px; font-weight:800;'>📊 Công Cụ Chia Target Đa Nền Tảng</h3>", unsafe_allow_html=True)
            
            # Lấy dữ liệu từ Đám mây về
            dt_data = db.get("daily_targets", {})
            dt_cfg = dt_data.get("config", {})
            dt_mts = dt_data.get("metrics", {})
            
            def s_float(val):
                if val is None or str(val).strip() == "": return 0.0
                try: return float(str(val).replace('.', '').replace(',', ''))
                except: return 0.0

            if st.session_state.is_admin or "TARGET KPI" in perms:
                with st.expander("⚙️ NHẬP LIỆU & CẤU HÌNH", expanded=True):
                    with st.form("target_form"):
                        st.markdown("**1. CẤU HÌNH CHUNG**")
                        c1, c2 = st.columns(2)
                        nv = c1.number_input("👥 Tổng Số NV", value=int(s_float(dt_cfg.get("nv", 1))), min_value=1)
                        vac = c2.number_input("💉 Đã bán Vắc Xin (VNĐ)", value=int(s_float(dt_cfg.get("vac", 0))), step=100000)
                        
                        st.markdown("**2. CẤU HÌNH CA TRỰC**")
                        c3, c4, c5, c6 = st.columns(4)
                        pc1 = c3.number_input("☀️ CA 1: Tỷ lệ (%)", value=float(s_float(dt_cfg.get("pc1", 50.0))))
                        ng1 = c4.number_input("☀️ CA 1: Số người", value=int(s_float(dt_cfg.get("ng1", 1))), min_value=1)
                        pc2 = c5.number_input("🌙 CA 2: Tỷ lệ (%)", value=float(s_float(dt_cfg.get("pc2", 50.0))))
                        ng2 = c6.number_input("🌙 CA 2: Số người", value=int(s_float(dt_cfg.get("ng2", 1))), min_value=1)
                        
                        st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)
                        st.markdown("**3. THIẾT LẬP CHỈ SỐ**")
                        
                        metrics = ["Doanh Số (VNĐ)", "Tổng Số Bill", "Cắt Liều", "Tỷ Lệ HOT", "Tỷ Lệ FS", "Tỷ Lệ 5 Sao"]
                        new_mts = {}
                        
                        for m in metrics:
                            st.markdown(f"<span style='color:#0ea5e9; font-weight:bold;'>{m}</span>", unsafe_allow_html=True)
                            m_data = dt_mts.get(m, {})
                            colA, colB, colC = st.columns(3)
                            
                            g = colA.number_input(f"Gốc ({m})", value=s_float(m_data.get("g", 0)), key=f"g_{m}", label_visibility="collapsed")
                            p = colB.number_input(f"% Đạt ({m})", value=s_float(m_data.get("p", 100)), key=f"p_{m}", label_visibility="collapsed")
                            n = colC.number_input(f"Ngày cần ({m})", value=s_float(m_data.get("n", 0)), key=f"n_{m}", label_visibility="collapsed")
                            new_mts[m] = {"g": g, "p": p, "n": n}
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.form_submit_button("⚡ TÍNH TOÁN & LƯU LÊN ĐÁM MÂY", type="primary", use_container_width=True):
                            if pc1 + pc2 != 100:
                                st.error("❌ Tổng tỷ lệ 2 ca phải bằng 100%!")
                            else:
                                new_config = {"nv": str(nv), "vac": str(vac), "pc1": str(pc1), "ng1": str(ng1), "pc2": str(pc2), "ng2": str(ng2)}
                                save_mts = {}
                                
                                fmt = lambda x: f"{int(x)}" if float(x).is_integer() else f"{float(x)}"
                                
                                for m in metrics:
                                    g_val = new_mts[m]["g"]
                                    p_val = new_mts[m]["p"]
                                    n_val = new_mts[m]["n"]
                                    
                                    # Công thức trừ Vắc xin
                                    t_val = (g_val * p_val) / 100
                                    if m == "Doanh Số (VNĐ)":
                                        t_val = t_val - vac
                                        if t_val < 0: t_val = 0
                                        
                                    save_mts[m] = {"g": fmt(g_val), "p": fmt(p_val), "t": fmt(t_val), "n": fmt(n_val)}
                                
                                update_firebase("daily_targets", {"config": new_config, "metrics": save_mts})
                                st.success("✅ Đã tính toán và đồng bộ về máy tính ở Shop!")
                                time.sleep(1)
                                st.rerun()

                # --- BẢNG HIỂN THỊ KẾT QUẢ ---
                st.markdown("<br><b>📊 KẾT QUẢ PHÂN BỔ (Tự động cập nhật)</b>", unsafe_allow_html=True)
                t1, t2 = st.tabs(["👤 BẢNG CÁ NHÂN", "🏪 BẢNG CA TRỰC"])
                
                nv_cur = int(s_float(dt_cfg.get("nv", 1)) or 1)
                pc1_cur = float(s_float(dt_cfg.get("pc1", 50)))
                ng1_cur = int(s_float(dt_cfg.get("ng1", 1)) or 1)
                pc2_cur = float(s_float(dt_cfg.get("pc2", 50)))
                ng2_cur = int(s_float(dt_cfg.get("ng2", 1)) or 1)

                res1_data, res2_data = [], []
                
                for m in metrics:
                    m_data = dt_mts.get(m, {})
                    val_t = s_float(m_data.get("t", 0))
                    val_n = s_float(m_data.get("n", 0))
                    
                    thang_1 = round(val_t / nv_cur) if nv_cur > 0 else 0
                    ngay_1 = round(val_n / nv_cur) if nv_cur > 0 else 0
                    
                    ca1_t = val_n * (pc1_cur / 100)
                    ca2_t = val_n * (pc2_cur / 100)
                    
                    ca1_1 = round(ca1_t / ng1_cur) if ng1_cur > 0 else 0
                    ca2_1 = round(ca2_t / ng2_cur) if ng2_cur > 0 else 0
                    
                    fm = lambda num, is_ds: f"{int(num):,}".replace(",", ".") + (" đ" if is_ds else "")
                    is_ds = (m == "Doanh Số (VNĐ)")
                    
                    res1_data.append({"Chỉ Số": m, "THÁNG / 1 NV": fm(thang_1, is_ds), "NGÀY / 1 NV": fm(ngay_1, is_ds)})
                    res2_data.append({"Chỉ Số": m, "Tổng Ngày": fm(val_n, is_ds), f"CA 1 (Tổng)": fm(round(ca1_t), is_ds), f"1 Người CA 1": fm(ca1_1, is_ds), f"CA 2 (Tổng)": fm(round(ca2_t), is_ds), f"1 Người CA 2": fm(ca2_1, is_ds)})
                    
                with t1: st.dataframe(pd.DataFrame(res1_data), hide_index=True, use_container_width=True)
                with t2: st.dataframe(pd.DataFrame(res2_data), hide_index=True, use_container_width=True)

        # ==========================================
        # 3. TAB LỊCH ECOM
        # ==========================================
        elif selected_tab == "🛒 LỊCH ECOM":
            st.markdown("<h3 style='margin-top: 0px; margin-bottom: 25px; font-weight:800;'>🛒 Bảng Phân Phối Ca Trực Khối ECOM</h3>", unsafe_allow_html=True)
            ecom_data = db.get("ecom_history", {})
            
            if st.session_state.is_admin or "SỬA LỊCH ECOM" in edit_perms:
                if st.button("🔄 ĐẢO NHÂN VIÊN TỪ SÁNG QUA CHIỀU", type="primary", use_container_width=True):
                    new_ecom = {}
                    for d in ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"]:
                        val = ecom_data.get(d, {})
                        if isinstance(val, dict): new_ecom[d] = {"Sáng": val.get("Chiều", ""), "Chiều": val.get("Sáng", "")}
                        elif isinstance(val, str): new_ecom[d] = {"Sáng": "", "Chiều": val}
                    update_firebase("ecom_history", new_ecom)
                    st.success("Đã đảo ca Ecom thành công!"); time.sleep(1); st.rerun()
                    
            if not ecom_data: st.info("Lịch Ecom hiện tại trống.")
            else:
                days = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"]
                ecom_list = []
                for d in days:
                    val = ecom_data.get(d, {})
                    if isinstance(val, str) and val.strip(): ecom_list.append({"Thứ / Ngày": d, "Trực Sáng": val.strip(), "Trực Chiều": "-"})
                    elif isinstance(val, dict):
                        s = val.get("Sáng", "").strip(); c = val.get("Chiều", "").strip()
                        if s or c: ecom_list.append({"Thứ / Ngày": d, "Trực Sáng": s if s else "-", "Trực Chiều": c if c else "-"})
                st.dataframe(pd.DataFrame(ecom_list), hide_index=True, use_container_width=True)

        # ==========================================
        # 4. TAB THI TRƯỜNG & QUỸ SHOP
        # ==========================================
        elif selected_tab == "📍 THI TRƯỜNG":
            st.markdown("<h3 style='margin-top: 0px; margin-bottom: 25px; font-weight:800;'>📍 Bản Đồ Phân Công Công Tác Thị Trường</h3>", unsafe_allow_html=True)
            market_data = db.get("market_history", {})
            if not market_data: st.info("Chưa có lịch phân phối.")
            else:
                market_list = [{"Kế hoạch Ngày": d, "📍 Địa Điểm": inf.get("dia_diem", ""), "👥 Tuyến": ", ".join(inf.get("nhan_vien", []))} for d, inf in market_data.items()]
                st.dataframe(pd.DataFrame(market_list), hide_index=True, use_container_width=True)

        elif selected_tab == "💰 SỔ QUỸ SHOP":
            st.markdown("<h3 style='margin-top: 0px; margin-bottom: 25px; font-weight:800;'>💰 Sổ Theo Dõi Thu Chi</h3>", unsafe_allow_html=True)
            qs = db.get("quy_shop", {})
            tong_thu = sum(float(i.get("amount", 0)) for i in qs.values() if i.get("type") == "Thu")
            tong_chi = sum(float(i.get("amount", 0)) for i in qs.values() if i.get("type") == "Chi")
            st.metric("🏦 TỒN QUỸ", format_vnd(tong_thu - tong_chi))
            c1, c2 = st.columns(2)
            c1.metric("🟢 TỔNG THU", format_vnd(tong_thu)); c2.metric("🔴 TỔNG CHI", format_vnd(tong_chi))
            
            if st.session_state.is_admin or "QUẢN LÝ QUỸ SHOP" in edit_perms:
                with st.expander("➕ HÀNH ĐỘNG GHI CHỨNG TỪ", expanded=False):
                    with st.form("fund_form", clear_on_submit=True):
                        f_type = st.selectbox("Phân loại", ["Thu", "Chi"])
                        f_amt = st.number_input("Giá trị (VNĐ)", min_value=0, step=50000)
                        f_desc = st.text_input("Nội dung diễn giải")
                        if st.form_submit_button("LƯU PHIẾU", type="primary", use_container_width=True):
                            if f_amt > 0 and f_desc:
                                update_firebase("quy_shop", {str(int(time.time() * 1000)): {"date": (datetime.utcnow() + timedelta(hours=7)).strftime("%d/%m/%Y %H:%M"), "type": f_type, "amount": f_amt, "desc": f_desc, "user": st.session_state.user}})
                                st.success("Thành công!"); time.sleep(0.5); st.rerun()
                            else: st.error("❌ Không được bỏ trống!")
            
            if qs:
                quy_list = [{"Mã CT": f"...{tid[-4:]}", "Thời Gian": tx.get("date", ""), "Phân Loại": "➕ Thu" if tx.get("type") == "Thu" else "➖ Chi", "Giá Trị": f"{float(tx.get('amount', 0)):,.0f} ₫".replace(",", "."), "Lý Do": tx.get("desc", ""), "Người Lập": tx.get("user", "")} for tid, tx in sorted(qs.items(), key=lambda x: x[0], reverse=True)]
                st.dataframe(pd.DataFrame(quy_list), hide_index=True, use_container_width=True)
                if st.session_state.is_admin or "QUẢN LÝ QUỸ SHOP" in edit_perms:
                    c_sel, c_del = st.columns([3, 1])
                    xoa_id = c_sel.selectbox("Chọn mã hủy:", [tx["Mã CT"] for tx in quy_list], label_visibility="collapsed")
                    if c_del.button("❌ HỦY", type="primary", use_container_width=True):
                        delete_firebase(f"quy_shop/{[tid for tid in qs.keys() if tid[-4:] == xoa_id[-4:]][0]}")
                        st.success("Đã xóa!"); time.sleep(0.5); st.rerun()

        # ==========================================
        # 5. TAB AI TƯ VẤN (CẬP NHẬT MỚI NHẤT)
        # ==========================================
        elif selected_tab == "🤖 AI TƯ VẤN":
            st.markdown("<h3 style='margin-top: 0px; margin-bottom: 25px; font-weight:800;'>🤖 Trợ Lý AI Tư Vấn Y Khoa</h3>", unsafe_allow_html=True)
            
            if "vaccine_chat" not in st.session_state:
                st.session_state.vaccine_chat = [{"role": "assistant", "content": "Chào bạn! Tôi là Bác sĩ và Dược sĩ lâm sàng cấp cao. Bạn cần hỗ trợ phân tích ca bệnh khó, thông tin chi tiết về thuốc hay phác đồ vắc xin?"}]

            chat_container = st.container()
            with chat_container:
                for msg in st.session_state.vaccine_chat:
                    with st.chat_message(msg["role"]): st.markdown(msg["content"])

            if prompt := st.chat_input("Nhập câu hỏi về thuốc, vắc xin hoặc ca lâm sàng..."):
                st.session_state.vaccine_chat.append({"role": "user", "content": prompt})
                with chat_container:
                    with st.chat_message("user"): st.markdown(prompt)
                    with st.chat_message("assistant"):
                        placeholder = st.empty()
                        placeholder.markdown("⏳ Đang phân tích dữ liệu y khoa...")
                        
                        k_list = db.get("settings", {}).get("api_keys", [])
                        if not k_list: reply = "❌ Hệ thống chưa có API Key."
                        else:
                            messages = [{"role": "system", "content": "Bạn là Bác sĩ và Dược sĩ lâm sàng cấp cao tại Việt Nam, chuyên gia hàng đầu về Thuốc và Vắc xin. Nhiệm vụ của bạn là giải đáp chuyên sâu các câu hỏi y khoa, bao gồm cả những ca lâm sàng khó, tương tác thuốc phức tạp. Yêu cầu: Văn phong chuyên nghiệp, đanh thép, bám sát y học thực chứng. Phân tích rõ ràng về cơ chế, dược động học, tương tác thuốc, chống chỉ định, và phác đồ. TUYỆT ĐỐI KHÔNG dùng văn phong dịch máy. Bắt buộc dùng đúng thuật ngữ y khoa/dược khoa chuẩn Việt Nam. Trình bày logic, chia mục thật rõ ràng. TUYỆT ĐỐI KHÔNG dùng emoji."}]
                            for m in st.session_state.vaccine_chat[-8:]:
                                if m["role"] == "user": 
                                    messages.append({"role": "user", "content": m["content"]})
                                elif m["role"] == "assistant" and "Chào bạn! Tôi là" not in m["content"] and "⏳" not in m["content"] and "❌" not in m["content"]:
                                    messages.append({"role": "assistant", "content": m["content"]})
                                    
                            payload = {"model": "llama-3.3-70b-versatile", "messages": messages, "temperature": 0.3}
                            suc = False
                            reply = "❌ Máy chủ AI đang bận."
                            
                            for k in k_list:
                                if suc: break
                                try:
                                    headers = {"Authorization": f"Bearer {k}", "Content-Type": "application/json"}
                                    r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=20)
                                    if r.status_code == 200:
                                        reply = "".join(c for c in r.json()['choices'][0]['message']['content'] if ord(c)<=0xFFFF)
                                        suc = True; break
                                    else:
                                        reply = f"❌ LỖI API ({r.status_code}): {r.text}"
                                except Exception as e: 
                                    reply = f"❌ LỖI MẠNG: {str(e)}"
                                    continue
                                        
                        placeholder.markdown(reply)
                        st.session_state.vaccine_chat.append({"role": "assistant", "content": reply})

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️ Làm Mới Cuộc Trò Chuyện", type="secondary", use_container_width=True):
                st.session_state.vaccine_chat = [{"role": "assistant", "content": "Chào bạn! Tôi là Bác sĩ chuyên gia tư vấn Vắc xin. Bạn cần hỗ trợ thông tin gì về các loại vắc xin, phác đồ tiêm hay chống chỉ định không?"}]
                st.rerun()

        # ==========================================
        # 6. TAB QUẢN TRỊ ADMIN
        # ==========================================
        elif selected_tab == "👥 QUẢN TRỊ ADMIN":
            st.markdown("<h3 style='margin-top: 0px; margin-bottom: 25px; font-weight:800;'>⚙️ Trung Tâm Điều Hành Quản Trị Hệ Thống</h3>", unsafe_allow_html=True)
            pending = db.get("pending_users", {})
            if pending:
                for pu, pinfo in pending.items():
                    with st.container():
                        c1, c2, c3 = st.columns([4, 2, 2])
                        c1.markdown(f"**👤 Tài khoản: {pu}**")
                        if c2.button("✅ Phê duyệt", key=f"ok_{pu}", type="primary", use_container_width=True):
                            pwd = pinfo.get("pass", "123456") if isinstance(pinfo, dict) else pinfo
                            update_firebase(f"users/{pu}", {"pass": pwd, "role": "user", "permissions": ["XEM LỊCH", "TÍCH LŨY"], "edit_permissions": []})
                            delete_firebase(f"pending_users/{pu}"); st.rerun()
                        if c3.button("❌ Bác bỏ", key=f"rej_{pu}", use_container_width=True):
                            delete_firebase(f"pending_users/{pu}"); st.rerun()
            
            st.divider()
            users = db.get("users", {})
            for u, uinfo in users.items():
                if uinfo.get("role") != "admin":
                    with st.expander(f"👤 Cấu hình quyền cho: {u}"):
                        current_perms = uinfo.get("permissions", [])
                        current_edits = uinfo.get("edit_permissions", [])
                        
                        view_options = ["XEM LỊCH", "TÍCH LŨY", "QUÉT AI KPI", "TARGET KPI", "CHIA DATA", "THỊ TRƯỜNG", "HOÀN TÁC", "DANH BẠ", "LẬP HÀNG", "XUẤT EXCEL", "GỬI ZALO", "QUỸ SHOP", "LỊCH ECOM", "AI TƯ VẤN"]
                        new_perms = st.multiselect("Bật/tắt các Tab hiển thị trên điện thoại:", view_options, default=[p for p in current_perms if p in view_options], key=f"perm_{u}")
                        
                        edit_options = ["SỬA SỐ KPI", "UP ẢNH KPI", "CHIA LỊCH TỰ ĐỘNG", "UP ẢNH LỊCH TRỰC", "SỬA LỊCH ECOM", "SỬA THỊ TRƯỜNG", "QUẢN LÝ QUỸ SHOP", "ĐẢO TÊN CA"]
                        new_edits = st.multiselect("Bật/tắt quyền thao tác trực tiếp:", edit_options, default=[p for p in current_edits if p in edit_options], key=f"edit_{u}")
                        
                        if st.button("💾 LƯU PHÂN QUYỀN", key=f"save_{u}", type="primary", use_container_width=True):
                            update_firebase(f"users/{u}", {"permissions": new_perms, "edit_permissions": new_edits})
                            st.success(f"Đã cập nhật!"); time.sleep(0.5); st.rerun()
