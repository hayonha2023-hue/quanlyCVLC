import streamlit as st
import requests
import time
import io
import base64
from PIL import Image, ImageOps

st.set_page_config(page_title="HTCV Web System", layout="wide", initial_sidebar_state="expanded")

FIREBASE_URL = "https://htcv-5c857-default-rtdb.firebaseio.com/htcv.json"

def fetch_data():
    try:
        r = requests.get(FIREBASE_URL)
        if r.status_code == 200: return r.json() or {}
    except: pass
    return {}

def update_firebase_user(path, data):
    try: requests.patch(f"{FIREBASE_URL.replace('.json', '')}/{path}.json", json=data)
    except: pass

def delete_firebase_user(path):
    try: requests.delete(f"{FIREBASE_URL.replace('.json', '')}/{path}.json")
    except: pass

# ==========================================
# 1. HỆ THỐNG ĐĂNG NHẬP
# ==========================================
if "user" not in st.session_state or not st.session_state.user:
    st.markdown("<h2 style='text-align: center; color: #0ea5e9; margin-top: 50px;'>HỆ THỐNG QUẢN TRỊ HTCV</h2>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2.form("login_form"):
        user_in = st.text_input("👤 Tài khoản").strip()
        pass_in = st.text_input("🔑 Mật khẩu", type="password").strip()
        if st.form_submit_button("🚀 ĐĂNG NHẬP", use_container_width=True):
            if not user_in or not pass_in:
                st.error("Vui lòng nhập đầy đủ thông tin!")
            else:
                db = fetch_data()
                users = db.get("users", {})
                
                is_valid = False
                
                if user_in in users and str(users[user_in].get("pass")) == pass_in:
                    is_valid = True
                elif user_in.lower() == "admin" and (pass_in == "123456" or pass_in == "admin"):
                    is_valid = True
                    user_in = "admin" 
                    if "admin" not in users:
                        update_firebase_user("users/admin", {"pass": "123456", "role": "admin"})
                
                if is_valid:
                    st.session_state.user = user_in
                    st.session_state.current_user = user_in
                    st.session_state.db = db
                    
                    u_info = users.get(user_in, {})
                    st.session_state.current_shop = u_info.get("shop_id", "Shop Chính (Mặc định)")
                    role = str(u_info.get("role", "")).lower()
                    
                    st.session_state.is_super_admin = (user_in.lower() == "admin")
                    st.session_state.is_admin = (role == "admin" or user_in.lower() == "admin")
                    
                    st.success("✅ Đăng nhập thành công!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("❌ Sai tài khoản hoặc mật khẩu! (Nếu quên, hãy gõ tài khoản: admin, mật khẩu: 123456)")
    st.stop()

# ==========================================
# THIẾT LẬP THÔNG TIN KHI ĐÃ ĐĂNG NHẬP
# ==========================================
user_id = st.session_state.user
db = st.session_state.get("db", {})
u_info = db.get("users", {}).get(user_id, {})

if "show_bg" not in st.session_state: st.session_state.show_bg = False
if "show_pass" not in st.session_state: st.session_state.show_pass = False
if "theme" not in st.session_state: st.session_state.theme = "Light"

def close_settings_panels():
    st.session_state.show_bg = False
    st.session_state.show_pass = False

# ==========================================
# 2. THANH MENU BÊN TRÁI (SIDEBAR)
# ==========================================
with st.sidebar:
    st.markdown(f"### 👤 {str(user_id).upper()}")
    st.markdown(f"📍 {st.session_state.get('current_shop', 'Shop Chính (Mặc định)')}")
    st.markdown("<hr style='margin: 10px 0px;'>", unsafe_allow_html=True)
    
    menu_options = ["🛒 Lịch Ecom", "💰 Quỹ Shop", "📋 Xem Lịch", "📈 Theo Dõi KPI", "📊 Chia Target", "📍 Thị Trường", "🤖 AI Tư Vấn", "👥 Quản Trị Admin"]
    menu = st.radio("MAIN MENU", menu_options, label_visibility="collapsed", on_change=close_settings_panels)
    
    st.markdown("<br><hr style='border-color: rgba(150,150,150,0.1); margin: 10px 0px;'>", unsafe_allow_html=True)
    
    if st.button("🖼️ Đổi hình nền", use_container_width=True):
        st.session_state.show_bg = not st.session_state.show_bg
        st.session_state.show_pass = False

    if st.button("🔑 Đổi mật khẩu", use_container_width=True):
        st.session_state.show_pass = not st.session_state.show_pass
        st.session_state.show_bg = False
    
    theme_label = "🌙 Giao diện Tối" if st.session_state.theme == "Light" else "☀️ Giao diện Sáng"
    if st.button(theme_label, use_container_width=True):
        st.session_state.theme = "Dark" if st.session_state.theme == "Light" else "Light"
        st.rerun()
        
    if st.button("🚪 Đăng xuất", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# ==========================================
# 3. ĐIỀU HƯỚNG CHÍNH MÀN HÌNH
# ==========================================
if st.session_state.show_bg:
    st.info("🖼️ ĐỔI HÌNH NỀN CÁ NHÂN (Tự động áp dụng sau khi tải xong)")
    bg_up = st.file_uploader("Chọn ảnh (Hệ thống tự nén cho nhẹ)", type=["png", "jpg", "jpeg"])
    c_bg1, c_bg2, c_bg3 = st.columns(3)
    
    if bg_up:
        if c_bg1.button("💾 ÁP DỤNG", type="primary", use_container_width=True):
            img = Image.open(bg_up)
            img = ImageOps.exif_transpose(img)
            img.thumbnail((1920, 1080))
            buffered = io.BytesIO()
            img.convert("RGB").save(buffered, format="JPEG", quality=85)
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            update_firebase_user(f"users/{user_id}/bg_image", img_str)
            st.session_state.db["users"][user_id]["bg_image"] = img_str
            st.session_state.show_bg = False
            st.success("Thành công!"); time.sleep(1); st.rerun()
            
    current_bg = u_info.get("bg_image", "")
    if current_bg:
        if c_bg2.button("🗑️ XÓA NỀN", use_container_width=True):
            delete_firebase_user(f"users/{user_id}/bg_image")
            st.session_state.db["users"][user_id]["bg_image"] = ""
            st.session_state.show_bg = False
            st.success("Đã xóa nền!"); time.sleep(1); st.rerun()
            
    if c_bg3.button("❌ ĐÓNG CÀI ĐẶT", use_container_width=True):
        st.session_state.show_bg = False
        st.rerun()

elif st.session_state.show_pass:
    st.info("🔑 THAY ĐỔI MẬT KHẨU")
    c_p1, c_p2 = st.columns(2)
    old_p = c_p1.text_input("Nhập mật khẩu cũ", type="password")
    new_p = c_p2.text_input("Nhập mật khẩu mới", type="password")
    
    c_btn1, c_btn2, c_btn3 = st.columns(3)
    if c_btn1.button("💾 CẬP NHẬT", type="primary", use_container_width=True):
        if old_p == str(u_info.get("pass", "")):
            update_firebase_user(f"users/{user_id}/pass", new_p)
            st.success("Đổi thành công! Đang đăng xuất...")
            time.sleep(1.5)
            st.session_state.clear()
            st.rerun()
        else:
            st.error("❌ Mật khẩu cũ sai!")
            
    if c_btn2.button("❌ ĐÓNG", use_container_width=True):
        st.session_state.show_pass = False
        st.rerun()

else:
    if menu == "🛒 Lịch Ecom":
        try: from views.ecom import render_ecom; render_ecom()
        except Exception as e: st.warning(f"Tính năng đang bảo trì: {e}")
    elif menu == "💰 Quỹ Shop":
        try: from views.fund import render_fund; render_fund()
        except Exception as e: st.warning(f"Tính năng đang bảo trì: {e}")
    elif menu == "📋 Xem Lịch":
        try: from views.schedule import render_schedule; render_schedule()
        except Exception as e: st.warning(f"Tính năng đang bảo trì: {e}")
    elif menu == "📈 Theo Dõi KPI":
        try: from views.kpi import render_kpi; render_kpi()
        except Exception as e: st.warning(f"Tính năng đang bảo trì: {e}")
    elif menu == "📊 Chia Target":
        try: from views.target import render_target; render_target()
        except Exception as e: st.warning(f"Tính năng đang bảo trì: {e}")
    elif menu == "📍 Thị Trường":
        try: from views.market import render_market; render_market()
        except Exception as e: st.warning(f"Tính năng đang bảo trì: {e}")
    elif menu == "🤖 AI Tư Vấn":
        try: from views.ai_chat import render_ai_chat; render_ai_chat()
        except Exception as e: st.warning(f"Tính năng đang bảo trì: {e}")
    elif menu == "👥 Quản Trị Admin":
        try: from views.admin import render_admin; render_admin()
        except Exception as e: st.warning(f"Tính năng đang bảo trì: {e}")

# ==========================================
# 4. CSS ĐIỀU KHIỂN GIAO DIỆN SÁNG/TỐI (ĐÃ FIX TÀNG HÌNH CHỮ)
# ==========================================
current_bg = u_info.get("bg_image", "")

if st.session_state.theme == "Dark" or current_bg:
    bg_sidebar = "rgba(14, 17, 23, 0.85)" if current_bg else "#262730"
    bg_main = "rgba(0, 0, 0, 0.65)" if current_bg else "#0e1117"
    text_global = "#ffffff"
    btn_bg = "rgba(255, 255, 255, 0.1)" if current_bg else "#333333"
    btn_text = "#ffffff"
else:
    bg_sidebar = "#f0f2f6"
    bg_main = "#ffffff"
    text_global = "#111827"
    btn_bg = "#ffffff"
    btn_text = "#111827"

css = f"""
<style>
    /* 1. MÀU CHỮ CHO TOÀN BỘ CÁC THÀNH PHẦN THANH MENU BÊN TRÁI */
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {{
        color: {text_global} !important;
    }}
    [data-testid="stSidebar"] {{ background-color: {bg_sidebar} !important; }}
    
    /* 2. MÀU CHỮ CHO CÁC TAB TIÊU ĐỀ, FORM VÀ TEXT CƠ BẢN */
    [data-testid="stTabs"] button p,
    [data-testid="stTabs"] button span,
    .stMarkdown p, 
    .stMarkdown li,
    label p, 
    h1, h2, h3, h4, h5, h6 {{
        color: {text_global} !important;
    }}
    
    /* 3. NÚT BẤM CÀI ĐẶT */
    .stButton > button {{
        background-color: {btn_bg} !important;
        color: {btn_text} !important;
        border: 1px solid rgba(150, 150, 150, 0.4) !important;
    }}
    .stButton > button p, .stButton > button span {{
        color: {btn_text} !important;
    }}
    
    /* 4. LỚP BỌC THÉP CHO BẢNG LỊCH TRỰC NỀN TRẮNG (VÀ CÁC THẺ TRẮNG KHÁC) */
    /* Phải để ở dưới cùng để ghi đè các luật màu trắng ở trên, nhưng tuyệt đối không ép thẻ SPAN để giữ màu chữ "Ca Chiều" (Đỏ) / "Ca Sáng" (Xanh) */
    [style*="background-color: white" i] p,
    [style*="background-color: white" i] div,
    [style*="background: white" i] p,
    [style*="background: white" i] div,
    [style*="background-color: #fff" i] p,
    [style*="background-color: #fff" i] div,
    [style*="background-color: #ffffff" i] p,
    [style*="background-color: #ffffff" i] div {{
        color: #111827 !important;
    }}
"""

if current_bg:
    css += f"""
    .stApp {{
        background-image: url("data:image/jpeg;base64,{current_bg}") !important;
        background-size: cover !important;
        background-attachment: fixed !important;
        background-position: center !important;
    }}
    [data-testid="stHeader"] {{ background-color: transparent !important; }}
    
    /* Lớp kính mờ lót dưới */
    div.block-container {{
        background-color: {bg_main} !important;
        border-radius: 15px; padding: 2rem !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    }}
    """
else:
    bg_solid = "#0e1117" if st.session_state.theme == "Dark" else "#ffffff"
    css += f"""
    .stApp, .main, [data-testid="stHeader"] {{ background-color: {bg_solid} !important; }}
    div.block-container {{ background-color: transparent !important; box-shadow: none; }}
    """

css += "</style>"
st.markdown(css, unsafe_allow_html=True)
