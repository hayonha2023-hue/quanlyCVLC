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

# ==========================================
# 2. THANH MENU BÊN TRÁI (SIDEBAR)
# ==========================================
with st.sidebar:
    st.markdown(f"### 👤 {str(user_id).upper()}")
    st.markdown(f"📍 {st.session_state.get('current_shop', 'Shop Chính (Mặc định)')}")
    st.markdown("<hr style='margin: 10px 0px;'>", unsafe_allow_html=True)
    
    menu_options = ["🛒 Lịch Ecom", "💰 Quỹ Shop", "📋 Xem Lịch", "📈 Theo Dõi KPI", "📊 Chia Target", "📍 Thị Trường", "🤖 AI Tư Vấn", "👥 Quản Trị Admin"]
    menu = st.radio("MAIN MENU", menu_options, label_visibility="collapsed")
    
    st.markdown("<br><hr style='border-color: rgba(150,150,150,0.1); margin: 10px 0px;'>", unsafe_allow_html=True)
    
    # NÚT ĐỔI HÌNH NỀN
    if st.button("🖼️ Đổi hình nền", use_container_width=True):
        st.session_state.show_bg = not st.session_state.show_bg
        st.session_state.show_pass = False

    # NÚT ĐỔI MẬT KHẨU
    if st.button("🔑 Đổi mật khẩu", use_container_width=True):
        st.session_state.show_pass = not st.session_state.show_pass
        st.session_state.show_bg = False
    
    # NÚT ĐỔI SÁNG/TỐI (Đã được khôi phục)
    theme_label = "🌙 Giao diện Tối" if st.session_state.theme == "Light" else "☀️ Giao diện Sáng"
    if st.button(theme_label, use_container_width=True):
        st.session_state.theme = "Dark" if st.session_state.theme == "Light" else "Light"
        st.rerun()
        
    if st.button("🚪 Đăng xuất", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# ==========================================
# 3. XỬ LÝ FORM CÀI ĐẶT (HIỂN THỊ CHÍNH GIỮA)
# ==========================================
if st.session_state.show_bg:
    st.info("🖼️ ĐỔI HÌNH NỀN CÁ NHÂN (Tự động áp dụng sau khi tải xong)")
    bg_up = st.file_uploader("Chọn ảnh (Hệ thống tự nén cho nhẹ)", type=["png", "jpg", "jpeg"])
    c_bg1, c_bg2 = st.columns(2)
    
    if bg_up:
        if c_bg1.button("💾 ÁP DỤNG MỚI", type="primary", use_container_width=True):
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
        if c_bg2.button("🗑️ XÓA NỀN ĐỂ VỀ MẶC ĐỊNH", use_container_width=True):
            delete_firebase_user(f"users/{user_id}/bg_image")
            st.session_state.db["users"][user_id]["bg_image"] = ""
            st.session_state.show_bg = False
            st.success("Đã xóa nền!"); time.sleep(1); st.rerun()
            
    st.stop() 

if st.session_state.show_pass:
    st.info("🔑 THAY ĐỔI MẬT KHẨU")
    c_p1, c_p2 = st.columns(2)
    old_p = c_p1.text_input("Nhập mật khẩu cũ", type="password")
    new_p = c_p2.text_input("Nhập mật khẩu mới", type="password")
    
    if st.button("💾 CẬP NHẬT MẬT KHẨU", type="primary"):
        if old_p == str(u_info.get("pass", "")):
            update_firebase_user(f"users/{user_id}/pass", new_p)
            st.success("Đổi thành công! Đang đăng xuất để áp dụng...")
            time.sleep(1.5)
            st.session_state.clear()
            st.rerun()
        else:
            st.error("❌ Mật khẩu cũ không chính xác!")
    st.stop()

# ==========================================
# 4. ĐIỀU HƯỚNG VÀO CÁC MODULE CHỨC NĂNG
# ==========================================
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
# 5. MÃ LỆNH ĐIỀU KHIỂN GIAO DIỆN & HÌNH NỀN
# ==========================================
theme_css = ""
if st.session_state.theme == "Dark":
    theme_css = """
    <style>
        /* Ép toàn bộ nền thành màu đen và chữ thành màu trắng */
        .stApp, .main, [data-testid="stHeader"] { background-color: #0e1117 !important; color: #fafafa !important; }
        [data-testid="stSidebar"] { background-color: #262730 !important; }
        p, h1, h2, h3, h4, h5, h6, label, span { color: #fafafa !important; }
        .stTextInput>div>div>input { color: #fafafa !important; background-color: #262730 !important; }
        .stSelectbox>div>div>div { color: #fafafa !important; background-color: #262730 !important; }
        .stDataFrame { filter: invert(0.85) hue-rotate(180deg); } /* Làm dịu màu bảng */
    </style>
    """

current_bg = u_info.get("bg_image", "")
bg_css = ""
if current_bg:
    bg_css = f"""
    <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{current_bg}");
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
        }}
        [data-testid="stSidebar"] {{ background-color: rgba(14, 17, 23, 0.85) !important; }}
        [data-testid="stHeader"] {{ background-color: transparent !important; }}
    </style>
    """

# Chèn CSS để bắt buộc đổi màu
st.markdown(theme_css + bg_css, unsafe_allow_html=True)
