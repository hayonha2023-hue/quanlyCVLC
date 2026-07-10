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
# 1. CẤU HÌNH GIAO DIỆN & SIÊU HIỆU ỨNG CSS CHUẨN UX/UI
# ==========================================
st.set_page_config(page_title="HTCV System", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

FIREBASE_URL = "https://htcv-5c857-default-rtdb.firebaseio.com/htcv.json"

# --- HÀM LẤY DỮ LIỆU TỔNG QUÁT ---
def get_full_data():
    try:
        r = requests.get(FIREBASE_URL, timeout=5)
        return r.json() if r.status_code == 200 and r.json() else {}
    except: return {}

# --- HỆ THỐNG ĐIỀU HƯỚNG SHOP (MULTI-TENANT) ---
def get_db_path(path):
    shop = st.session_state.get("current_shop", "Shop Chính (Mặc định)")
    if shop and shop != "Shop Chính (Mặc định)":
        return f"shops/{shop}/{path}"
    return path

def update_firebase(path, data):
    requests.patch(f"{FIREBASE_URL.replace('.json', '')}/{get_db_path(path)}.json", json=data)

def delete_firebase(path):
    requests.delete(f"{FIREBASE_URL.replace('.json', '')}/{get_db_path(path)}.json")

def update_firebase_global(path, data): # Dành cho lưu User/Settings toàn cục
    requests.patch(f"{FIREBASE_URL.replace('.json', '')}/{path}.json", json=data)

def delete_firebase_global(path):
    requests.delete(f"{FIREBASE_URL.replace('.json', '')}/{path}.json")

def format_vnd(amount): return f"{amount:,.0f} ₫".replace(",", ".")
def get_hash(text): return hashlib.md5(text.encode('utf-8')).hexdigest()

# THUẬT TOÁN XỬ LÝ SỐ CHUẨN XÁC
def s_float(val):
    if val is None or str(val).strip() == "": return 0.0
    if isinstance(val, (int, float)): return float(val)
    s = str(val).strip()
    if s.endswith(".0") and s.count(".") == 1:
        try: return float(s)
        except: pass
    try: return float(s.replace('.', '').replace(',', ''))
    except: return 0.0
    
def fmt_dot(val):
    v = s_float(val)
    if v == 0: return ""
    if v.is_integer(): return f"{int(v):,}".replace(",", ".")
    return f"{v:,.1f}".replace(",", ".")

def fmt_num(val):
    v = s_float(val)
    return f"{int(v)}" if v.is_integer() else f"{v}"

def logout():
    st.session_state.user = None
    st.session_state.current_shop = None
    st.session_state.is_admin = False
    st.session_state.is_super_admin = False
    st.query_params.clear()
    st.rerun()

# KHỞI TẠO BIẾN SESSION
if "user" not in st.session_state:
    st.session_state.user = None
    st.session_state.current_shop = None
    st.session_state.is_admin = False
    st.session_state.is_super_admin = False
    st.session_state.page = "login"

full_db = get_full_data()

# TỰ ĐỘNG ĐĂNG NHẬP QUA LINK
if st.session_state.user is None:
    if "u" in st.query_params and "t" in st.query_params:
        u_url = st.query_params["u"]
        t_url = st.query_params["t"]
        global_users = full_db.get("users", {})
        if u_url in global_users and get_hash(global_users[u_url]["pass"]) == t_url:
            
            # --- ÉP CỨNG: TÀI KHOẢN 'admin' MẶC ĐỊNH LUÔN LÀ CHÚA TỂ ---
            if u_url == "admin":
                st.session_state.is_super_admin = True
                st.session_state.is_admin = True
                st.session_state.user = u_url
                st.session_state.current_shop = st.query_params.get("s", "Shop Chính (Mặc định)")
            elif st.query_params.get("sa") == "1" and global_users[u_url].get("role") == "admin":
                st.session_state.is_super_admin = True
                st.session_state.is_admin = True
                st.session_state.user = u_url
                st.session_state.current_shop = st.query_params.get("s", "Shop Chính (Mặc định)")
            else:
                st.session_state.is_super_admin = False
                st.session_state.is_admin = (global_users[u_url].get("role") == "admin")
                st.session_state.user = u_url
                st.session_state.current_shop = global_users[u_url].get("shop_id", "Shop Chính (Mặc định)")

# ==========================================
# 2. XỬ LÝ CSS & THEME KÍNH MỜ
# ==========================================
base_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"]  { font-family: 'Inter', sans-serif !important; }
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
[data-testid="stHeaderActionElements"], .stDeployButton, #manage-app-button {display: none !important;}
.stTabs [data-baseweb="tab-list"] { gap: 8px; padding: 6px; border-radius: 12px; border-bottom: none; }
.stTabs [data-baseweb="tab"] { border-radius: 8px !important; padding: 10px 16px; border: none !important; background-color: transparent; color: #94a3b8 !important; transition: all 0.3s ease; }
.stTextInput input { border-radius: 8px; padding: 12px 15px; transition: all 0.3s ease; font-weight: 500; }
.stTextInput input:focus { border-color: #0ea5e9 !important; box-shadow: 0 0 0 2px rgba(14, 165, 233, 0.2) !important; }
[data-testid="stExpander"] { box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); border-radius: 12px; margin-bottom: 12px; transition: all 0.3s ease; }
[data-testid="stExpander"] summary p { font-weight: 700; font-size: 15px; }
.stButton > button { border-radius: 8px; font-weight: 700; padding: 10px 0; transition: all 0.3s ease; }
.stButton > button[kind="primary"] { background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%); border: none; color: white; }
.stButton > button[kind="primary"]:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(2, 132, 199, 0.4); }

/* VÁ LỖI CẢM ỨNG MENU CHUẨN XÁC 100% */
[data-testid="stSidebar"] div[role="radiogroup"] > label { 
    background-color: transparent !important; 
    border-radius: 12px !important; 
    padding: 12px 16px !important; 
    margin-bottom: 8px !important; 
    cursor: pointer; 
    transition: all 0.2s !important; 
    display: flex !important;
    align-items: center !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label:hover { background-color: rgba(14, 165, 233, 0.15) !important; }
[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] { background-color: rgba(14, 165, 233, 0.25) !important; border-left: 4px solid #0ea5e9 !important; }

/* CHỈ ẩn cái chấm tròn hiển thị, TUYỆT ĐỐI không ẩn cái thẻ Input gốc để giữ cảm ứng */
[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child > div { display: none !important; }
[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child { margin-right: 0px !important; }

[data-testid="stSidebar"] div[role="radiogroup"] > label p { font-size: 15px !important; font-weight: 700 !important; margin: 0 !important; width: 100% !important; }
</style>
"""
st.markdown(base_css, unsafe_allow_html=True)

if "theme" not in st.session_state: st.session_state.theme = "Dark" 

bg_b64 = full_db.get("users", {}).get(st.session_state.user, {}).get("bg_image", "") if st.session_state.user else ""

if st.session_state.theme == "Light":
    bg_sb = "rgba(255, 255, 255, 0.92)" if bg_b64 else "#ffffff"
    bg_el = "rgba(255, 255, 255, 0.92)" if bg_b64 else "#ffffff"
    theme_css = f"""<style>
    [data-testid="stAppViewContainer"] {{ background-color: #f1f5f9 !important; }}
    [data-testid="stSidebar"] {{ background-color: {bg_sb} !important; backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border-right: 1px solid rgba(0,0,0,0.1); }} 
    .stApp {{ color: #0f172a !important; }} 
    .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, label, span, th, td {{ color: #0f172a !important; }} 
    [data-testid="stMetricValue"] {{ color: #0284c7 !important; }} 
    [data-testid="stMetric"], [data-testid="stForm"], [data-testid="stExpander"] {{ background-color: {bg_el} !important; backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid rgba(0,0,0,0.15) !important; }} 
    button[kind="secondary"] {{ background-color: {bg_el} !important; color: #0284c7 !important; border: 2px solid #e2e8f0 !important; font-weight: 700 !important; }} 
    button[kind="secondary"]:hover {{ background-color: #f0f9ff !important; border-color: #0ea5e9 !important; }} 
    .stTabs [data-baseweb="tab-list"] {{ background-color: rgba(226, 232, 240, 0.95) !important; backdrop-filter: blur(16px); }} 
    .stTabs [aria-selected="true"] {{ background-color: #ffffff !important; color: #0284c7 !important; font-weight: 800 !important; }} 
    .stTextInput input {{ background-color: rgba(255, 255, 255, 0.9) !important; color: #0f172a !important; border: 1px solid #94a3b8 !important; }} 
    [data-testid="stSidebar"] div[role="radiogroup"] > label p, [data-testid="stExpander"] summary p {{ color: #0f172a !important; }}
    </style>"""
else:
    bg_sb = "rgba(15, 23, 42, 0.92)" if bg_b64 else "#0f172a"
    bg_el = "rgba(30, 41, 59, 0.92)" if bg_b64 else "#1e293b"
    theme_css = f"""<style>
    [data-testid="stAppViewContainer"] {{ background-color: #090d16 !important; }}
    [data-testid="stSidebar"] {{ background-color: {bg_sb} !important; backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border-right: 1px solid rgba(255,255,255,0.1); }} 
    .stApp {{ color: #f8fafc !important; }} 
    .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, label, span, th, td {{ color: #f8fafc !important; }} 
    [data-testid="stMetricValue"] {{ color: #38bdf8 !important; }} 
    [data-testid="stMetric"], [data-testid="stForm"], [data-testid="stExpander"] {{ background-color: {bg_el} !important; backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid rgba(255,255,255,0.15) !important; }} 
    button[kind="secondary"] {{ background-color: {bg_el} !important; color: #38bdf8 !important; border: 2px solid #334155 !important; font-weight: 700 !important; }} 
    button[kind="secondary"]:hover {{ background-color: #111827 !important; border-color: #38bdf8 !important; }}
    .stTabs [data-baseweb="tab-list"] {{ background-color: rgba(15, 23, 42, 0.95) !important; backdrop-filter: blur(16px); }}
    .stTextInput input {{ background-color: rgba(15, 23, 42, 0.9) !important; color: #f8fafc !important; border: 1px solid #475569 !important; }} 
    [data-testid="stSidebar"] div[role="radiogroup"] > label p {{ color: #f8fafc !important; }}
    </style>"""

if bg_b64:
    overlay = "rgba(255, 255, 255, 0.35)" if st.session_state.theme == "Light" else "rgba(0, 0, 0, 0.55)"
    theme_css += f"""<style>[data-testid="stAppViewContainer"] {{ background: linear-gradient({overlay}, {overlay}), url('data:image/jpeg;base64,{bg_b64}') center center / cover no-repeat fixed !important; }} .stApp > header {{ background-color: transparent !important; }}</style>"""

st.markdown(theme_css, unsafe_allow_html=True)

# ==========================================
# 3. MÀN HÌNH ĐĂNG NHẬP
# ==========================================
if st.session_state.user is None:
    _, col_center, _ = st.columns([1, 1.8, 1])
    with col_center:
        st.markdown("<br>", unsafe_allow_html=True)
        import os
        img_path = "Logo.png" if os.path.exists("Logo.png") else ("Logo.ico" if os.path.exists("Logo.ico") else "")
        if img_path:
            with open(img_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
                logo_html = f"<img src='data:image/png;base64,{b64}' style='width: 100px; height: 100px; border-radius: 24px; box-shadow: 0 10px 30px rgba(14, 165, 233, 0.4); margin-bottom: 15px; border: 1px solid rgba(14,165,233,0.3);'>"
        else:
            logo_html = """<div style='display: inline-flex; align-items: center; justify-content: center; width: 85px; height: 85px; border-radius: 50%; background: rgba(14, 165, 233, 0.05); border: 2px solid rgba(14, 165, 233, 0.4); box-shadow: 0 0 25px rgba(14, 165, 233, 0.15); margin-bottom: 15px;'><svg width="38" height="38" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><rect x="9" y="10" width="6" height="6" rx="1" ry="1"></rect><path d="M12 10v-2a2 2 0 1 1 4 0v2"></path></svg></div>"""

        st.markdown(f"<div style='text-align: center; margin-bottom: 25px;'>{logo_html}<h1 style='color: #0ea5e9; font-size: 2.5rem; font-weight:900; margin: 0; letter-spacing: 1.5px;'>HTCV SaaS Platform</h1></div>", unsafe_allow_html=True)
        
        if st.session_state.page == "login":
            with st.form("login_form"):
                st.markdown("<h4 style='text-align: center; margin-bottom: 10px; font-weight:800; color: #64748b;'>ĐĂNG NHẬP HỆ THỐNG</h4>", unsafe_allow_html=True)
                
                u = st.text_input("👤 TÀI KHOẢN").strip().lower()
                p = st.text_input("🔑 MẬT KHẨU", type="password")
                st.markdown("<br>", unsafe_allow_html=True)
                
                if st.form_submit_button("🚀 ĐĂNG NHẬP", type="primary", use_container_width=True):
                    if u and p:
                        global_users = full_db.get("users", {})
                        if u in global_users and global_users[u]["pass"] == p:
                            
                            # --- TỰ ĐỘNG KHÓA QUYỀN CHÚA TỂ CHO ADMIN ---
                            if u == "admin":
                                st.session_state.is_super_admin = True
                                st.session_state.is_admin = True
                                st.session_state.user = u
                                st.session_state.current_shop = "Shop Chính (Mặc định)"
                                st.query_params["sa"] = "1"
                                st.query_params["u"] = u
                                st.query_params["t"] = get_hash(p)
                                st.success("👑 Đăng nhập quyền Admin Tổng thành công!")
                                time.sleep(1); st.rerun()
                            else:
                                st.session_state.is_super_admin = False
                                st.session_state.is_admin = (global_users[u].get("role") == "admin")
                                st.session_state.user = u
                                st.session_state.current_shop = global_users[u].get("shop_id", "Shop Chính (Mặc định)")
                                st.query_params["u"] = u
                                st.query_params["t"] = get_hash(p)
                                st.rerun()
                                
                        elif u in full_db.get("pending_users", {}): st.warning("⏳ Tài khoản đang chờ duyệt!")
                        else: st.error("❌ Sai thông tin đăng nhập!")
                    else: st.error("❌ Vui lòng nhập đầy đủ thông tin!")
                    
            c1, c2 = st.columns(2)
            if c1.button("📝 Đăng ký tài khoản", use_container_width=True): st.session_state.page = "register"; st.rerun()
            if c2.button("❓ Quên mật khẩu", use_container_width=True): st.session_state.page = "forgot"; st.rerun()

        elif st.session_state.page == "register":
            with st.form("reg_form"):
                st.markdown("<h4 style='text-align: center; margin-bottom: 30px; font-weight:800; color: #64748b;'>ĐĂNG KÝ TÀI KHOẢN MỚI</h4>", unsafe_allow_html=True)
                new_shop = st.text_input("🏢 MÃ SHOP (Nếu bạn làm ở Shop nhánh, để trống nếu ở Shop Chính)").strip().lower()
                new_u = st.text_input("Tên đăng nhập").strip().lower()
                new_p = st.text_input("Mật khẩu truy cập", type="password")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("GỬI YÊU CẦU", type="primary", use_container_width=True):
                    if new_u and new_p:
                        req_shop = new_shop if new_shop else "Shop Chính (Mặc định)"
                        update_firebase_global(f"pending_users/{new_u}", {"pass": new_p, "shop_id": req_shop})
                        st.success("✅ Đã gửi yêu cầu tham gia! Vui lòng báo Admin duyệt.")
                    else: st.error("Nhập đủ thông tin!")
            if st.button("⬅ Quay lại", use_container_width=True): st.session_state.page = "login"; st.rerun()

        elif st.session_state.page == "forgot":
            with st.form("forgot_form"):
                st.markdown("<h4 style='text-align: center; margin-bottom: 30px; font-weight:800; color: #64748b;'>KHÔI PHỤC MẬT KHẨU</h4>", unsafe_allow_html=True)
                u = st.text_input("Tài khoản cần khôi phục").strip().lower()
                new_p = st.text_input("Mật khẩu mới", type="password")
                secret = st.text_input("Mã xác thực Admin Tổng", type="password")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("XÁC NHẬN", type="primary", use_container_width=True):
                    if secret == "admin123":
                        update_firebase_global(f"users/{u}/pass", new_p)
                        st.success("✅ Đổi thành công! Vui lòng đăng nhập lại.")
                    else: st.error("❌ Mã bảo mật sai!")
            if st.button("⬅ Quay lại", use_container_width=True): st.session_state.page = "login"; st.rerun()

# ==========================================
# 4. MÀN HÌNH CHÍNH & SIDEBAR
# ==========================================
else:
    # LOAD DỮ LIỆU ĐỘC LẬP TÙY VÀO SHOP ĐANG ĐỨNG
    if st.session_state.current_shop == "Shop Chính (Mặc định)":
        db = full_db
    else:
        db = full_db.get("shops", {}).get(st.session_state.current_shop, {})

    u_info = full_db.get("users", {}).get(st.session_state.user, {})
    if st.session_state.is_super_admin:
        perms = ["XEM LỊCH", "TÍCH LŨY", "CHIA TARGET", "THỊ TRƯỜNG", "QUỸ SHOP", "LỊCH ECOM", "AI TƯ VẤN"]
        edit_perms = ["SỬA SỐ KPI", "UP ẢNH KPI", "CHIA LỊCH TỰ ĐỘNG", "UP ẢNH LỊCH TRỰC", "SỬA LỊCH ECOM", "SỬA THỊ TRƯỜNG", "QUẢN LÝ QUỸ SHOP", "ĐẢO TÊN CA", "TÍNH TARGET"]
    else:
        perms = u_info.get("permissions", [])
        edit_perms = u_info.get("edit_permissions", []) 
    
    tab_dict = {"🗓️ LỊCH TRỰC": "XEM LỊCH", "🛒 LỊCH ECOM": "LỊCH ECOM", "🎯 BẢNG KPI": "TÍCH LŨY", "📍 THI TRƯỜNG": "THỊ TRƯỜNG", "💰 SỔ QUỸ SHOP": "QUỸ SHOP", "📊 CHIA TARGET": "CHIA TARGET", "🤖 AI TƯ VẤN": "AI TƯ VẤN"}
    allowed_tabs = []
    hidden = full_db.get("settings", {}).get("hidden_features", [])

    if st.session_state.is_super_admin:
        # ĐẶC QUYỀN CHÚA TỂ: Nhìn thấy toàn bộ Tab trên Web
        allowed_tabs = list(tab_dict.keys()) + ["👥 QUẢN TRỊ ADMIN"]
    elif st.session_state.is_admin: 
        # ADMIN THƯỜNG: Bị ẩn các Tab theo lệnh Chúa Tể
        allowed_tabs = [k for k, v in tab_dict.items() if v not in hidden] + ["👥 QUẢN TRỊ ADMIN"]
    else: 
        allowed_tabs = [k for k, v in tab_dict.items() if (v in perms) and (v not in hidden)]

    if not allowed_tabs:
        st.error("Tài khoản chưa được cấp quyền truy cập hoặc chức năng đang bị ẩn.")
        if st.button("Thoát"): logout()
    else:
        with st.sidebar:
            role_icon = "👑" if st.session_state.is_super_admin else ("⭐" if st.session_state.is_admin else "👤")
            st.markdown(f"<h2 style='text-align: center; color: #0ea5e9; font-weight:800; margin-bottom: 0;'>{role_icon} {st.session_state.user.upper()}</h2>", unsafe_allow_html=True)
            
            role_name = "ADMIN TỔNG HỆ THỐNG" if st.session_state.is_super_admin else ("QUẢN TRỊ SHOP" if st.session_state.is_admin else "NHÂN VIÊN CƠ SỞ")
            st.markdown(f"<p style='text-align: center; color: #64748b; font-size: 13px;'>{role_name}</p>", unsafe_allow_html=True)
            
            if st.session_state.is_super_admin:
                # BỌC THÉP: Chống lỗi văng App nếu chưa có Shop nhánh nào được tạo
                shops_data = full_db.get("shops", {})
                if not isinstance(shops_data, dict): shops_data = {}
                
                all_shops = ["Shop Chính (Mặc định)"] + list(shops_data.keys())
                if st.session_state.current_shop not in all_shops: all_shops.append(st.session_state.current_shop)
                
                st.markdown("<br>", unsafe_allow_html=True)
                new_shop = st.selectbox("🏢 ACTION: CHỌN MÃ SHOP", all_shops, index=all_shops.index(st.session_state.current_shop))
                if new_shop != st.session_state.current_shop:
                    st.session_state.current_shop = new_shop
                    st.query_params["s"] = new_shop
                    st.rerun()
                    
                with st.expander("➕ Tạo Mã Shop Mới", expanded=False):
                    ns = st.text_input("Nhập mã nhánh mới (vd: hcm)", placeholder="fpt_hcm", label_visibility="collapsed")
                    if st.button("Tạo Không Gian & Chuyển", use_container_width=True):
                        if ns:
                            update_firebase_global(f"shops/{ns}", {"created": True})
                            st.session_state.current_shop = ns
                            st.rerun()
            else:
                st.markdown(f"<p style='text-align: center; color: #10b981; font-weight: bold; font-size: 14px;'>📍 Không gian: {st.session_state.current_shop}</p>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            selected_tab = st.radio("MENU CHỨC NĂNG", allowed_tabs, label_visibility="collapsed")
            st.markdown("<br><hr style='border-color: rgba(150,150,150,0.1);'><br>", unsafe_allow_html=True)
            
            if st.button("🖼️ Đổi hình nền cá nhân", use_container_width=True):
                st.session_state.show_bg_setting = not st.session_state.get("show_bg_setting", False)
                st.session_state.show_pass = False
                st.session_state.force_close_sidebar = True

            if st.button("🔑 Cài đặt mật khẩu", use_container_width=True):
                st.session_state.show_pass = not st.session_state.get("show_pass", False)
                st.session_state.show_bg_setting = False
                st.session_state.force_close_sidebar = True
                
            theme_txt = "☀️ Giao diện Sáng" if st.session_state.theme == "Dark" else "🌙 Giao diện Tối"
            if st.button(theme_txt, use_container_width=True):
                st.session_state.theme = "Light" if st.session_state.theme == "Dark" else "Dark"
                st.session_state.force_close_sidebar = True
                
            if st.button("🚪 Đăng xuất", use_container_width=True): logout()

        # Logic thu gọn thanh Menu tự động sau khi chọn
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

        # XỬ LÝ ĐỔI HÌNH NỀN CÁ NHÂN
        if st.session_state.get("show_bg_setting", False):
            with st.container():
                st.markdown("<div style='padding: 22px; border-radius: 16px; background-color: rgba(14, 165, 233, 0.04); border: 1px solid rgba(14, 165, 233, 0.2); margin-bottom: 25px;'>", unsafe_allow_html=True)
                st.markdown("<h5 style='color:#0ea5e9; font-weight: bold; margin-top: 0;'>🖼️ TÙY CHỈNH HÌNH NỀN CÁ NHÂN</h5>", unsafe_allow_html=True)
                bg_up = st.file_uploader("Chọn ảnh từ máy (Nên chọn ảnh độ phân giải cao)", type=["png", "jpg", "jpeg"])
                c_bg1, c_bg2 = st.columns(2)
                
                if bg_up:
                    if c_bg1.button("💾 ÁP DỤNG", type="primary", use_container_width=True):
                        img = Image.open(bg_up)
                        img = ImageOps.exif_transpose(img)
                        img.thumbnail((1920, 1080))
                        buffered = io.BytesIO()
                        img.convert("RGB").save(buffered, format="JPEG", quality=85)
                        update_firebase_global(f"users/{st.session_state.user}/bg_image", base64.b64encode(buffered.getvalue()).decode())
                        st.session_state.show_bg_setting = False
                        st.success("Thành công!"); time.sleep(1); st.rerun()
                
                if u_info.get("bg_image"):
                    if c_bg2.button("🗑️ XÓA ẢNH", use_container_width=True):
                        delete_firebase_global(f"users/{st.session_state.user}/bg_image")
                        st.session_state.show_bg_setting = False
                        st.success("Đã xóa!"); time.sleep(1); st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

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
                        update_firebase_global(f"users/{st.session_state.user}/pass", new_p)
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
                            delete_firebase("kpi_images") # <-- Thêm dòng này để dọn rác
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
                            delete_firebase("schedule_images") # <-- Thêm dòng này để dọn rác
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
                hidden_ft = full_db.get("settings", {}).get("hidden_features", [])
                lich_list = []
                for date_str, shifts in history.items():
                    row_data = {
                        "Mốc Thời Gian": date_str,
                        "Ca Sáng": ", ".join(shifts.get("Sáng", [])) if shifts.get("Sáng") else "-",
                        "Ca Chiều": ", ".join(shifts.get("Chiều", [])) if shifts.get("Chiều") else "-"
                    }
                    if "CA 10H30" not in hidden_ft: row_data["Ca Đêm (10h30)"] = ", ".join(shifts.get("10h30", [])) if shifts.get("10h30") else "-"
                    lich_list.append(row_data)
                st.dataframe(pd.DataFrame(lich_list), hide_index=True, use_container_width=True)

        # ==========================================
        # 2.5 TAB CHIA TARGET
        # ==========================================
        elif selected_tab == "📊 CHIA TARGET":
            st.markdown("<h3 style='margin-top: 0px; margin-bottom: 25px; font-weight:800;'>📊 Công Cụ Chia Target Đa Nền Tảng</h3>", unsafe_allow_html=True)
            
            components.html("""
            <script>
            const doc = window.parent.document;
            if (!doc.getElementById("live-format-money")) {
                let s = doc.createElement("script");
                s.id = "live-format-money";
                s.innerHTML = `
                    document.addEventListener('input', function(e) {
                        if (e.isTrusted && e.target && e.target.tagName === 'INPUT') {
                            let p = e.target.placeholder || "";
                            if (p.includes("1.500.000") || p.includes("Mục tiêu") || p.includes("Ngày") || p.includes("Đã bán") || p.includes("Còn lại") || p.includes("Mỗi ngày") || p.includes("VD: 30") || p.includes("để trống") || p.includes("Gợi ý")) {
                                let oldVal = e.target.value;
                                let oldCursor = e.target.selectionStart;
                                let raw = oldVal.replace(/[^0-9]/g, '');
                                if (raw) {
                                    let formatted = Number(raw).toLocaleString('vi-VN').replace(/,/g, '.');
                                    if (formatted !== oldVal) {
                                        let nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                                        nativeSetter.call(e.target, formatted);
                                        e.target.dispatchEvent(new Event('input', { bubbles: true }));
                                        let diff = formatted.length - oldVal.length;
                                        e.target.setSelectionRange(oldCursor + diff, oldCursor + diff);
                                    }
                                }
                            }
                        }
                    });
                `;
                doc.body.appendChild(s);
            }
            </script>
            """, height=0, width=0)

            dt_data = db.get("daily_targets", {})
            dt_cfg = dt_data.get("config", {})
            dt_mts = dt_data.get("metrics", {})

            if st.session_state.is_admin or "TÍNH TARGET" in edit_perms:
                st.markdown("<h5 style='color:#0ea5e9; font-weight: bold;'>⚙️ BẢNG NHẬP LIỆU TÙY CHỈNH (Nảy số tự động)</h5>", unsafe_allow_html=True)
                
                tab_chung, tab_ca, tab_chiso = st.tabs(["⚙️ 1. CHUNG", "👥 2. CA TRỰC", "🎯 3. CHỈ SỐ"])
                
                with tab_chung:
                    c1, c2 = st.columns(2)
                    nv_str = c1.text_input("👥 Tổng NV", value=fmt_num(dt_cfg.get("nv", 1)))
                    nv = s_float(nv_str)
                    nc_str = c2.text_input("⏳ Số ngày còn lại", value=fmt_num(dt_cfg.get("nc", 30)), placeholder="VD: 30")
                    nc = s_float(nc_str)
                    
                    c3, c4 = st.columns(2)
                    vac_str = c3.text_input("💉 Bán Vắc Xin (VNĐ)", value=fmt_dot(dt_cfg.get("vac", 0)), placeholder="VD: 1.500.000")
                    vac = s_float(vac_str)
                    st.markdown("""<style> .stCheckbox {padding-top: 30px;} </style>""", unsafe_allow_html=True)
                    vac_chk = c4.checkbox("☑️ Trừ Vắc Xin", value=dt_cfg.get("vac_chk", True))
                    
                with tab_ca:
                    c5, c6 = st.columns(2)
                    pc1_str = c5.text_input("☀️ CA 1 (%)", value=fmt_num(dt_cfg.get("pc1", 50)))
                    pc1 = s_float(pc1_str)
                    ng1_str = c6.text_input("☀️ CA 1 (Người)", value=fmt_num(dt_cfg.get("ng1", 1)))
                    ng1 = s_float(ng1_str)
                    
                    c7, c8 = st.columns(2)
                    pc2_str = c7.text_input("🌙 CA 2 (%)", value=fmt_num(dt_cfg.get("pc2", 50)))
                    pc2 = s_float(pc2_str)
                    ng2_str = c8.text_input("🌙 CA 2 (Người)", value=fmt_num(dt_cfg.get("ng2", 1)))
                    ng2 = s_float(ng2_str)
                    
                live_mts = {}
                with tab_chiso:
                    st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
                    metrics = ["Doanh Số (VNĐ)", "Tổng Số Bill", "Cắt Liều", "Tỷ Lệ HOT", "Tỷ Lệ FS", "Tỷ Lệ 5 Sao"]
                    icon_map = {"Doanh Số (VNĐ)": "💰", "Tổng Số Bill": "🧾", "Cắt Liều": "💊", "Tỷ Lệ HOT": "🔥", "Tỷ Lệ FS": "⚡", "Tỷ Lệ 5 Sao": "⭐"}
                    
                    for m in metrics:
                        m_data = dt_mts.get(m, {})
                        icon = icon_map.get(m, "🔹")
                        
                        with st.expander(f"{icon} {m}", expanded=False):
                            r1c1, r1c2 = st.columns([1.5, 1])
                            g_str = r1c1.text_input("Mục tiêu gốc", value=fmt_dot(m_data.get("g", 0)), key=f"g_{m}", placeholder="Mục tiêu...")
                            p_str = r1c2.text_input("% Đạt", value=fmt_num(m_data.get("p", 100)), key=f"p_{m}", placeholder="%...")
                            
                            r2c1, r2c2 = st.columns(2)
                            db_str = r2c1.text_input("Đã bán", value=fmt_dot(m_data.get("db", 0)), key=f"db_{m}", placeholder="Đã bán...")
                            
                            g_val = s_float(g_str)
                            p_val = s_float(p_str)
                            db_val = s_float(db_str)
                            
                            t_val = (g_val * p_val) / 100
                            if m == "Doanh Số (VNĐ)" and vac_chk:
                                t_val -= vac
                                
                            cl_val = t_val - db_val
                            if cl_val < 0: cl_val = 0
                            
                            auto_n = cl_val / nc if nc > 0 else 0
                            
                            r2c2.markdown(f"<div style='font-size:14px; margin-bottom:5px; color:#94a3b8;'>Còn phải bán</div><div style='background-color: transparent; border: 1px solid #334155; padding: 10px; border-radius: 6px; color:#10b981; font-weight:bold;'>{fmt_dot(cl_val)}</div>", unsafe_allow_html=True)
                            
                            n_str = st.text_input("Mỗi ngày cần (Để trống máy tự chia, nhập số để đè)", value=m_data.get("n_str_saved", ""), placeholder=f"Gợi ý chia đều: {fmt_dot(auto_n)}", key=f"n_{m}")
                            
                            final_n = s_float(n_str) if n_str.strip() else auto_n
                            
                            live_mts[m] = {
                                "g": g_val, "p": p_val, "db": db_val,
                                "cl": cl_val, "n": final_n,
                                "g_str": g_str, "p_str": p_str, "db_str": db_str, "n_str": n_str
                            }
                    
                st.markdown("<br>", unsafe_allow_html=True)
                btn_c1, btn_c2 = st.columns([1, 1])
                
                del_btn = btn_c1.button("🗑️ XÓA SỐ TẠM", use_container_width=True)
                sub_btn = btn_c2.button("☁️ LƯU LÊN WEB", type="primary", use_container_width=True)
                
                if del_btn:
                    update_firebase("daily_targets", {"config": {}, "metrics": {}})
                    st.success("✅ Đã dọn sạch bảng chia Target!")
                    time.sleep(1)
                    st.rerun()

                if sub_btn:
                    if pc1 + pc2 != 100:
                        st.error("❌ Tổng tỷ lệ 2 ca phải bằng 100%!")
                    else:
                        fmt = lambda x: f"{int(x)}" if float(x).is_integer() else f"{float(x)}"
                        new_config = {"nv": fmt(nv), "vac": fmt(vac), "vac_chk": vac_chk, "nc": fmt(nc), "pc1": fmt(pc1), "ng1": fmt(ng1), "pc2": fmt(pc2), "ng2": fmt(ng2)}
                        save_mts = {}
                        
                        for m in metrics:
                            lm = live_mts[m]
                            save_mts[m] = {"g": fmt(lm["g"]), "p": fmt(lm["p"]), "db": fmt(lm["db"]), "cl": fmt(lm["cl"]), "n": fmt(lm["n"])}
                            save_mts[m]["n_str_saved"] = lm["n_str"]
                        
                        update_firebase("daily_targets", {"config": new_config, "metrics": save_mts})
                        st.success("✅ Đã lưu kết quả lên hệ thống để nhân viên cùng xem!")
                        time.sleep(1)
                        st.rerun()

            else:
                live_mts = {}
                nv = s_float(dt_cfg.get("nv", 1))
                pc1 = s_float(dt_cfg.get("pc1", 50))
                ng1 = s_float(dt_cfg.get("ng1", 1))
                pc2 = s_float(dt_cfg.get("pc2", 50))
                ng2 = s_float(dt_cfg.get("ng2", 1))
                
                for m in ["Doanh Số (VNĐ)", "Tổng Số Bill", "Cắt Liều", "Tỷ Lệ HOT", "Tỷ Lệ FS", "Tỷ Lệ 5 Sao"]:
                    m_data = dt_mts.get(m, {})
                    live_mts[m] = {
                        "cl": s_float(m_data.get("cl", 0)),
                        "n": s_float(m_data.get("n", 0))
                    }

            st.markdown("<br><b>📊 KẾT QUẢ PHÂN BỔ (Tự động cập nhật nhảy số)</b>", unsafe_allow_html=True)
            t1, t2 = st.tabs(["👤 BẢNG CÁ NHÂN", "🏪 BẢNG CA TRỰC"])
            
            nv_cur = int(nv or 1)
            pc1_cur = pc1
            ng1_cur = int(ng1 or 1)
            pc2_cur = pc2
            ng2_cur = int(ng2 or 1)

            res1_data, res2_data = [], []
            
            for m in ["Doanh Số (VNĐ)", "Tổng Số Bill", "Cắt Liều", "Tỷ Lệ HOT", "Tỷ Lệ FS", "Tỷ Lệ 5 Sao"]:
                val_cl = live_mts[m]["cl"] 
                val_n = live_mts[m]["n"]
                
                thang_1 = round(val_cl / nv_cur) if nv_cur > 0 else 0
                
                ca1_t = val_n * (pc1_cur / 100)
                ca2_t = val_n * (pc2_cur / 100)
                
                ca1_1 = round(ca1_t / ng1_cur) if ng1_cur > 0 else 0
                ca2_1 = round(ca2_t / ng2_cur) if ng2_cur > 0 else 0
                
                fm_res = lambda num, is_ds: f"{int(num):,}".replace(",", ".") + (" đ" if is_ds else "")
                is_ds = (m == "Doanh Số (VNĐ)")
                
                res1_data.append({"Chỉ Số": m, "CÒN PHẢI BÁN": fm_res(thang_1, is_ds)})
                res2_data.append({"Chỉ Số": m, "Mỗi Ngày Cần": fm_res(val_n, is_ds), f"CA 1 ({pc1_cur:g}%)": fm_res(round(ca1_t), is_ds), f"1 Người C1": fm_res(ca1_1, is_ds), f"CA 2 ({pc2_cur:g}%)": fm_res(round(ca2_t), is_ds), f"1 Người C2": fm_res(ca2_1, is_ds)})
                
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
            
            # Tính toán phân tách 3 loại
            tong_thu = sum(float(i.get("amount", 0)) for i in qs.values() if i.get("type") == "Thu")
            tong_chi = sum(float(i.get("amount", 0)) for i in qs.values() if i.get("type") == "Chi")
            tong_chi_rieng = sum(float(i.get("amount", 0)) for i in qs.values() if i.get("type") == "Chi riêng")
            
            # TỒN QUỸ TỰ ĐỘNG BỎ QUA CHI RIÊNG
            st.metric("🏦 TỒN QUỸ", format_vnd(tong_thu - tong_chi))
            
            c1, c2, c3 = st.columns(3)
            c1.metric("🟢 TỔNG THU", format_vnd(tong_thu))
            c2.metric("🔴 TỔNG CHI", format_vnd(tong_chi))
            c3.metric("🟠 CHI RIÊNG", format_vnd(tong_chi_rieng))
            
            if st.session_state.is_admin or "QUẢN LÝ QUỸ SHOP" in edit_perms:
                with st.expander("➕ HÀNH ĐỘNG GHI CHỨNG TỪ", expanded=False):
                    with st.form("fund_form", clear_on_submit=True):
                        f_type = st.selectbox("Phân loại", ["Thu", "Chi", "Chi riêng"])
                        f_amt = st.number_input("Giá trị (VNĐ)", min_value=0, step=50000)
                        f_desc = st.text_input("Nội dung diễn giải")
                        if st.form_submit_button("LƯU PHIẾU", type="primary", use_container_width=True):
                            if f_amt > 0 and f_desc:
                                update_firebase("quy_shop", {str(int(time.time() * 1000)): {"date": (datetime.utcnow() + timedelta(hours=7)).strftime("%d/%m/%Y %H:%M"), "type": f_type, "amount": f_amt, "desc": f_desc, "user": st.session_state.user}})
                                st.success("Thành công!"); time.sleep(0.5); st.rerun()
                            else: st.error("❌ Không được bỏ trống!")
            
            if qs:
                def get_tx_label(t):
                    if t == "Thu": return "➕ Thu"
                    if t == "Chi riêng": return "💸 Chi riêng"
                    return "➖ Chi"
                
                quy_list = [{"Mã CT": f"...{tid[-4:]}", "Thời Gian": tx.get("date", ""), "Phân Loại": get_tx_label(tx.get("type")), "Giá Trị": f"{float(tx.get('amount', 0)):,.0f} ₫".replace(",", "."), "Lý Do": tx.get("desc", ""), "Người Lập": tx.get("user", "")} for tid, tx in sorted(qs.items(), key=lambda x: x[0], reverse=True)]
                st.dataframe(pd.DataFrame(quy_list), hide_index=True, use_container_width=True)
                if st.session_state.is_admin or "QUẢN LÝ QUỸ SHOP" in edit_perms:
                    c_sel, c_del = st.columns([3, 1])
                    xoa_id = c_sel.selectbox("Chọn mã hủy:", [tx["Mã CT"] for tx in quy_list], label_visibility="collapsed")
                    if c_del.button("❌ HỦY", type="primary", use_container_width=True):
                        delete_firebase(f"quy_shop/{[tid for tid in qs.keys() if tid[-4:] == xoa_id[-4:]][0]}")
                        st.success("Đã xóa!"); time.sleep(0.5); st.rerun()

        # ==========================================
        # 5. TAB AI TƯ VẤN
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
                        
                        k_list = full_db.get("settings", {}).get("api_keys", [])
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
        # 6. TAB QUẢN TRỊ ADMIN (PHÂN QUYỀN ĐA NHÁNH)
        # ==========================================
        elif selected_tab == "👥 QUẢN TRỊ ADMIN":
            st.markdown("<h3 style='margin-top: 0px; margin-bottom: 25px; font-weight:800;'>⚙️ Trung Tâm Điều Hành Quản Trị Hệ Thống</h3>", unsafe_allow_html=True)
            
            # --- DANH SÁCH DUYỆT TÀI KHOẢN ---
            pending = full_db.get("pending_users", {})
            if pending:
                for pu, pinfo in pending.items():
                    req_shop = pinfo.get("shop_id", "Shop Chính (Mặc định)")
                    if st.session_state.is_super_admin or req_shop == st.session_state.current_shop:
                        with st.container():
                            c1, c2, c3 = st.columns([4, 2, 2])
                            c1.markdown(f"**👤 Xin duyệt:** {pu} (📍 {req_shop})")
                            if c2.button("✅ Phê duyệt", key=f"ok_{pu}", type="primary", use_container_width=True):
                                pwd = pinfo.get("pass", "123456") if isinstance(pinfo, dict) else pinfo
                                update_firebase_global(f"users/{pu}", {"pass": pwd, "role": "user", "shop_id": req_shop, "permissions": ["XEM LỊCH", "TÍCH LŨY"], "edit_permissions": []})
                                delete_firebase_global(f"pending_users/{pu}")
                                st.rerun()
                            if c3.button("❌ Bác bỏ", key=f"rej_{pu}", use_container_width=True):
                                delete_firebase_global(f"pending_users/{pu}")
                                st.rerun()
            
            st.divider()
            
            # --- DANH SÁCH QUẢN LÝ NHÂN VIÊN ĐÃ DUYỆT ---
            global_users = full_db.get("users", {})
            all_shops = ["Shop Chính (Mặc định)"] + list(full_db.get("shops", {}).keys())
            
            for u, uinfo in global_users.items():
                u_shop = uinfo.get("shop_id", "Shop Chính (Mặc định)")
                
                if st.session_state.is_super_admin or (u_shop == st.session_state.current_shop and uinfo.get("role") != "admin"):
                    with st.expander(f"👤 Cấu hình tài khoản: {u} (Vai trò: {uinfo.get('role', 'user')})"):
                        
                        new_shop = u_shop
                        new_role = uinfo.get("role", "user")
                        if st.session_state.is_super_admin:
                            col_s1, col_s2 = st.columns(2)
                            new_shop = col_s1.selectbox("Điều chuyển Shop:", all_shops, index=all_shops.index(u_shop) if u_shop in all_shops else 0, key=f"shop_{u}")
                            new_role = col_s2.selectbox("Cấp bậc:", ["user", "admin"], index=0 if uinfo.get("role")=="user" else 1, key=f"role_{u}")
                        
                        current_perms = uinfo.get("permissions", [])
                        current_edits = uinfo.get("edit_permissions", [])
                        
                        view_options = ["XEM LỊCH", "TÍCH LŨY", "QUÉT AI KPI", "CHIA TARGET", "CHIA DATA", "THỊ TRƯỜNG", "HOÀN TÁC", "DANH BẠ", "LẬP HÀNG", "XUẤT EXCEL", "GỬI ZALO", "QUỸ SHOP", "LỊCH ECOM", "AI TƯ VẤN"]
                        new_perms = st.multiselect("Bật/tắt các Tab hiển thị trên điện thoại:", view_options, default=[p for p in current_perms if p in view_options], key=f"perm_{u}")
                        
                        edit_options = ["SỬA SỐ KPI", "UP ẢNH KPI", "CHIA LỊCH TỰ ĐỘNG", "UP ẢNH LỊCH TRỰC", "SỬA LỊCH ECOM", "SỬA THỊ TRƯỜNG", "QUẢN LÝ QUỸ SHOP", "ĐẢO TÊN CA", "TÍNH TARGET"]
                        new_edits = st.multiselect("Bật/tắt quyền thao tác trực tiếp:", edit_options, default=[p for p in current_edits if p in edit_options], key=f"edit_{u}")
                        
                        if st.button("💾 LƯU CẤU HÌNH TÀI KHOẢN NÀY", key=f"save_{u}", type="primary", use_container_width=True):
                            update_firebase_global(f"users/{u}", {"pass": uinfo.get("pass"), "bg_image": uinfo.get("bg_image", ""), "role": new_role, "shop_id": new_shop, "permissions": new_perms, "edit_permissions": new_edits})
                            st.success(f"Đã cập nhật!"); time.sleep(0.5); st.rerun()
