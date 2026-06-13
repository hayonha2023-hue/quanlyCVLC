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
    [data-testid="stHeaderActionElements"] {display: none !important;}
    .stDeployButton {display: none !important;}
    #manage-app-button {display: none !important;}
    footer {display: none !important;}
    
    [data-testid="stForm"] {
        border-radius: 20px !important; border: 1px solid rgba(150, 150, 150, 0.15) !important;
        padding: 30px !important; background: rgba(255, 255, 255, 0.02) !important;
        backdrop-filter: blur(10px) !important; box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2) !important;
    }
    .stButton>button {
        border-radius: 12px !important; font-weight: 700 !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    .stButton>button:hover { transform: translateY(-2px) !important; box-shadow: 0 6px 15px rgba(14, 165, 233, 0.3) !important; }
    
    [data-testid="stMetric"] { border-radius: 18px !important; padding: 20px !important; border: 1px solid rgba(14, 165, 233, 0.15) !important; }
    [data-testid="stMetric"]:hover { transform: translateY(-4px) !important; border-color: #0ea5e9 !important; box-shadow: 0 12px 24px rgba(14, 165, 233, 0.15) !important; }
    [data-testid="stMetricValue"] { font-size: 2.2rem !important; font-weight: 800 !important; }
    [data-testid="stExpander"] { border-radius: 14px !important; overflow: hidden !important; border: 1px solid rgba(150, 150, 150, 0.12) !important; }

    [data-testid="stSidebar"] div[role="radiogroup"] > label {
        background-color: transparent !important; border-radius: 12px !important; padding: 14px 18px !important;
        margin-bottom: 10px !important; cursor: pointer; transition: all 0.2s !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label:hover { background-color: rgba(14, 165, 233, 0.08) !important; }
    [data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] {
        background-color: rgba(14, 165, 233, 0.15) !important; border-left: 5px solid #0ea5e9 !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child { display: none !important; }
    [data-testid="stSidebar"] div[role="radiogroup"] > label p { font-size: 16px !important; font-weight: 600 !important; }

    /* NÚT THOÁT ẢNH MÀU ĐỎ DÀNH CHO ĐIỆN THOẠI */
    div[data-testid="StyledFullScreenFrame"] button {
        top: 60px !important; right: 20px !important; width: 55px !important; height: 55px !important;
        background-color: rgba(239, 68, 68, 0.95) !important; border-radius: 50% !important;
        opacity: 1 !important; z-index: 9999999 !important; border: 2px solid white !important;
    }
    div[data-testid="StyledFullScreenFrame"] button svg { color: white !important; fill: white !important; width: 28px !important; height: 28px !important; }
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
        st.markdown("<h1 style='text-align: center; color: #0ea5e9; font-size: 2.8rem; font-weight:900;'>⚡ HTCV SYSTEM</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; margin-bottom: 40px; opacity: 0.6;'>Hệ Thống Quản Lý Số Cửa Hàng Chuyên Nghiệp</p>", unsafe_allow_html=True)
        
        if st.session_state.page == "login":
            with st.form("login_form"):
                st.markdown("<h4 style='text-align: center; margin-bottom: 25px; font-weight:800;'>XÁC THỰC TÀI KHOẢN</h4>", unsafe_allow_html=True)
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
                new_u = st.text_input("Tên đăng nhập").strip().lower()
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
                new_p = st.text_input("Mật khẩu mới", type="password")
                secret = st.text_input("Mã xác thực Admin")
                if st.form_submit_button("XÁC NHẬN", type="primary", use_container_width=True):
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
    edit_perms = u_info.get("edit_permissions", []) # Khai báo bộ quyền Edit mới
    
    tab_dict = {"🎯 BẢNG KPI": "TÍCH LŨY", "🗓️ LỊCH TRỰC": "XEM LỊCH", "🛒 LỊCH ECOM": "LỊCH ECOM", "📍 THI TRƯỜNG": "THỊ TRƯỜNG", "💰 SỔ QUỸ SHOP": "QUỸ SHOP"}
    allowed_tabs = []
    
    if st.session_state.is_admin: 
        allowed_tabs = list(tab_dict.keys()) + ["👥 QUẢN TRỊ ADMIN"]
    else: 
        allowed_tabs = [k for k, v in tab_dict.items() if v in perms]

    if not allowed_tabs:
        st.error("Tài khoản chưa được cấp quyền truy cập.")
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

        # LOGIC TỰ ĐỘNG THU GỌN SIDEBAR
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
            old_kpi_single = db.get("kpi_image", "")
            if old_kpi_single and not kpi_imgs: kpi_imgs = [old_kpi_single]
            
            # Kiểm tra quyền: Là Admin HOẶC được cấp quyền Sửa Tích Lũy
            if st.session_state.is_admin or "SỬA SỐ KPI" in edit_perms:
                with st.expander("📸 QUẢN LÝ ẢNH DANH MỤC KPI (Quyền thao tác)"):
                    st.markdown("💡 *Khi tải lên bộ ảnh mới, ảnh cũ sẽ TỰ ĐỘNG BỊ XÓA SẠCH.*")
                    uploaded_files = st.file_uploader("Chọn nhiều ảnh Bảng tính KPI", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="kpi_up")
                    
                    if 'rot_angles_kpi' not in st.session_state: st.session_state.rot_angles_kpi = {}
                        
                    if uploaded_files:
                        st.markdown("<p style='text-align: center; color: #0ea5e9; font-weight: bold; margin-top: 10px;'>👀 BẢN XEM TRƯỚC TỪNG ẢNH:</p>", unsafe_allow_html=True)
                        for i, up_file in enumerate(uploaded_files):
                            fname = up_file.name
                            if fname not in st.session_state.rot_angles_kpi: st.session_state.rot_angles_kpi[fname] = 0
                            preview_img = Image.open(up_file)
                            preview_img = ImageOps.exif_transpose(preview_img)
                            angle = st.session_state.rot_angles_kpi[fname]
                            if angle != 0: preview_img = preview_img.rotate(angle, expand=True)
                                
                            st.caption(f"Ảnh {i+1}: {fname}")
                            st.image(preview_img, use_container_width=True)
                            
                            if st.button(f"🔄 Xoay riêng ảnh {i+1} này 90 độ", key=f"rot_kpi_{i}_{fname}", use_container_width=True):
                                st.session_state.rot_angles_kpi[fname] = (st.session_state.rot_angles_kpi[fname] - 90) % 360
                                st.rerun()
                            st.markdown("<hr style='border-color: rgba(150,150,150,0.2);'>", unsafe_allow_html=True)
                            
                        if st.button("💾 LƯU BỘ ẢNH NÀY (GHI ĐÈ ẢNH CŨ)", type="primary", use_container_width=True, key="kpi_save"):
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
                                img_str = base64.b64encode(buffered.getvalue()).decode()
                                new_img_list.append(img_str)
                            
                            update_firebase("kpi_images", new_img_list)
                            if old_kpi_single: delete_firebase("kpi_image")
                            st.session_state.rot_angles_kpi = {} 
                            st.success(f"✅ Đã tải lên {len(new_img_list)} ảnh đúng chiều! Dữ liệu cũ đã bị xóa.")
                            time.sleep(1); st.rerun()
                            
                    if kpi_imgs:
                        if st.button("🗑️ Xóa vĩnh viễn TOÀN BỘ ảnh KPI hiện tại", type="primary", key="kpi_del"):
                            delete_firebase("kpi_images"); delete_firebase("kpi_image"); st.rerun()

            if kpi_imgs:
                with st.expander(f"📄 MỞ XEM BẢNG DANH MỤC HÀNG HÓA TÍNH KPI ({len(kpi_imgs)} trang)", expanded=False):
                    for idx, img_b64 in enumerate(kpi_imgs):
                        try:
                            st.markdown(f"<p style='text-align: center; color: #0ea5e9; font-weight: bold; margin-top: 15px; margin-bottom: 5px;'>Trang {idx + 1}</p>", unsafe_allow_html=True)
                            img_bytes = base64.b64decode(img_b64)
                            st.image(img_bytes, use_container_width=True)
                        except: st.error(f"Lỗi hiển thị ảnh trang {idx + 1}.")
                        
            st.markdown("<hr style='border-color: rgba(150,150,150,0.1); margin-top: 10px; margin-bottom: 20px;'>", unsafe_allow_html=True)
            
            # --- BẢNG SỐ LIỆU KPI ---
            kpi_node = db.get("kpi")
            if not isinstance(kpi_node, dict): kpi_node = {}
            kpi_data = kpi_node.get("emp")
            if isinstance(kpi_data, list): kpi_data = {str(i): v for i, v in enumerate(kpi_data) if v is not None}
            elif not isinstance(kpi_data, dict): kpi_data = {}
            
            if not kpi_data: st.info("Chưa có dữ liệu mục tiêu KPI tháng này.")
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

                # Quyền Sửa Số KPI
                if st.session_state.is_admin or "TÍCH LŨY" in edit_perms:
                    st.caption("💡 Chạm 2 lần vào ô 'Đã Bán (Số lượng)' để sửa nhanh.")
                    edited_df = st.data_editor(df_kpi, hide_index=True, disabled=["Nhân Viên", "Target Giao", "Còn Thiếu KPI"], use_container_width=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("💾 LƯU SỐ LIỆU SỬA ĐỔI", type="primary", use_container_width=True):
                        for idx, row in edited_df.iterrows():
                            update_firebase(f"kpi/emp/{row['Nhân Viên']}", {"sold": int(row["Đã Bán (Số lượng)"])})
                        st.success("Đã đồng bộ cập nhật lên hệ thống!"); time.sleep(0.5); st.rerun()
                else:
                    st.dataframe(df_kpi, hide_index=True, use_container_width=True)

        # ==========================================
        # 2. TAB LỊCH TRỰC
        # ==========================================
        elif selected_tab == "🗓️ LỊCH TRỰC":
            st.markdown("<h3 style='margin-top: 0px; margin-bottom: 25px; font-weight:800;'>🗓️ Bảng Phân Phối Lịch Trực Tuần</h3>", unsafe_allow_html=True)
            
            sched_imgs = db.get("schedule_images", [])
            if not isinstance(sched_imgs, list): sched_imgs = []
            old_single = db.get("schedule_image", "")
            if old_single and old_single not in sched_imgs: sched_imgs.insert(0, old_single)
            
            # Kiểm tra quyền Sửa Lịch
            if st.session_state.is_admin or "XEM LỊCH" in edit_perms:
                with st.expander("📸 QUẢN LÝ ẢNH BẢNG LỊCH TRỰC (Quyền thao tác)"):
                    st.markdown("💡 *Khi tải lên bộ ảnh mới, toàn bộ lịch cũ sẽ TỰ ĐỘNG BỊ XÓA SẠCH.*")
                    uploaded_files = st.file_uploader("Chọn bộ ảnh Lịch trực để thay thế", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="sched_up")
                    
                    if 'rot_angles_sched' not in st.session_state: st.session_state.rot_angles_sched = {}
                        
                    if uploaded_files:
                        st.markdown("<p style='text-align: center; color: #0ea5e9; font-weight: bold; margin-top: 10px;'>👀 BẢN XEM TRƯỚC TỪNG ẢNH:</p>", unsafe_allow_html=True)
                        for i, up_file in enumerate(uploaded_files):
                            fname = up_file.name
                            if fname not in st.session_state.rot_angles_sched: st.session_state.rot_angles_sched[fname] = 0
                            preview_img = Image.open(up_file)
                            preview_img = ImageOps.exif_transpose(preview_img)
                            angle = st.session_state.rot_angles_sched[fname]
                            if angle != 0: preview_img = preview_img.rotate(angle, expand=True)
                                
                            st.caption(f"Ảnh {i+1}: {fname}")
                            st.image(preview_img, use_container_width=True)
                            
                            if st.button(f"🔄 Xoay riêng ảnh {i+1} này 90 độ", key=f"rot_sched_{i}_{fname}", use_container_width=True):
                                st.session_state.rot_angles_sched[fname] = (st.session_state.rot_angles_sched[fname] - 90) % 360
                                st.rerun()
                            st.markdown("<hr style='border-color: rgba(150,150,150,0.2);'>", unsafe_allow_html=True)
                            
                        if st.button("💾 LƯU BỘ LỊCH NÀY (GHI ĐÈ LỊCH CŨ)", type="primary", use_container_width=True, key="sched_save"):
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
                                img_str = base64.b64encode(buffered.getvalue()).decode()
                                new_img_list.append(img_str)
                            
                            update_firebase("schedule_images", new_img_list)
                            if old_single: delete_firebase("schedule_image")
                            st.session_state.rot_angles_sched = {}
                            st.success(f"✅ Đã tải lên {len(new_img_list)} ảnh mới! Lịch cũ đã bị xóa sạch.")
                            time.sleep(1); st.rerun()
                            
                    if sched_imgs:
                        if st.button("🗑️ Xóa vĩnh viễn TOÀN BỘ lịch hiện tại", type="primary", key="sched_del"):
                            delete_firebase("schedule_images"); delete_firebase("schedule_image"); st.rerun()

            if sched_imgs:
                with st.expander(f"📄 MỞ XEM BỘ ẢNH LỊCH TRỰC ({len(sched_imgs)} trang)", expanded=False):
                    for idx, img_b64 in enumerate(sched_imgs):
                        try:
                            img_bytes = base64.b64decode(img_b64)
                            st.markdown(f"<p style='text-align: center; color: #0ea5e9; font-weight: bold; margin-top: 15px; margin-bottom: 5px;'>Trang {idx + 1}</p>", unsafe_allow_html=True)
                            st.image(img_bytes, use_container_width=True)
                        except: st.error(f"Lỗi hiển thị ảnh trang {idx + 1}.")
            
            st.markdown("<hr style='border-color: rgba(150,150,150,0.1); margin-top: 10px; margin-bottom: 20px;'>", unsafe_allow_html=True)
            history = db.get("detailed_history", {})
            if not history: st.info("Chưa có thông tin phân lịch tự động.")
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

        # ==========================================
        # 3. TAB LỊCH ECOM & THỊ TRƯỜNG (Chỉ xem)
        # ==========================================
        elif selected_tab == "🛒 LỊCH ECOM":
            st.markdown("<h3 style='margin-top: 0px; margin-bottom: 25px; font-weight:800;'>🛒 Bảng Phân Phối Ca Trực Khối ECOM</h3>", unsafe_allow_html=True)
            ecom_data = db.get("ecom_history", {})
            if not ecom_data: st.info("Lịch Ecom hiện tại trống.")
            else:
                days = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"]
                ecom_list = []
                for d in days:
                    val = ecom_data.get(d, {})
                    if isinstance(val, str) and val.strip(): ecom_list.append({"Thứ / Ngày": d, "Nhân Sự Trực Sáng": val.strip(), "Nhân Sự Trực Chiều": "-"})
                    elif isinstance(val, dict):
                        s = val.get("Sáng", "").strip()
                        c = val.get("Chiều", "").strip()
                        if s or c: ecom_list.append({"Thứ / Ngày": d, "Nhân Sự Trực Sáng": s if s else "-", "Nhân Sự Trực Chiều": c if c else "-"})
                if ecom_list: st.dataframe(pd.DataFrame(ecom_list), hide_index=True, use_container_width=True)
                else: st.info("Lịch Ecom hiện đang trống.")

        elif selected_tab == "📍 THI TRƯỜNG":
            st.markdown("<h3 style='margin-top: 0px; margin-bottom: 25px; font-weight:800;'>📍 Bản Đồ Phân Công Công Tác Thị Trường</h3>", unsafe_allow_html=True)
            market_data = db.get("market_history", {})
            if not market_data: st.info("Chưa có lịch phân phối thị trường.")
            else:
                days_order = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"]
                market_list = []
                for d in days_order:
                    if d in market_data:
                        inf = market_data[d]
                        market_list.append({"Kế hoạch Ngày": d, "📍 Địa Điểm Khảo Sát": inf.get("dia_diem", ""), "👥 Nhân Sự Tuyến Thị Trường": ", ".join(inf.get("nhan_vien", []))})
                if market_list: st.dataframe(pd.DataFrame(market_list), hide_index=True, use_container_width=True)
                else: st.info("Lịch điều phối thị trường đang trống.")

        # ==========================================
        # 4. TAB QUỸ SHOP
        # ==========================================
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
            
            # Quyền Sửa Sổ Quỹ
            if st.session_state.is_admin or "QUỸ SHOP" in edit_perms:
                with st.expander("➕ HÀNH ĐỘNG GHI CHỨNG TỪ THU / CHI MỚI (Quyền thao tác)", expanded=False):
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
            if not qs: st.caption("Chưa có biến động dòng tiền nào được ghi nhận.")
            else:
                quy_list = []
                for tx_id, tx in sorted(qs.items(), key=lambda x: x[0], reverse=True):
                    quy_list.append({
                        "Mã CT": f"...{tx_id[-4:]}",
                        "Thời Gian": tx.get("date", ""),
                        "Phân Loại": "➕ Thu Tiền" if tx.get("type") == "Thu" else "➖ Chi Tiền",
                        "Giá Trị": f"{float(tx.get('amount', 0)):,.0f} ₫".replace(",", "."),
                        "Lý Do Phát Sinh": tx.get("desc", ""),
                        "Người Lập Phiếu": tx.get("user", "")
                    })
                st.dataframe(pd.DataFrame(quy_list), hide_index=True, use_container_width=True)
                
                # Quyền Xóa Chứng Từ
                if st.session_state.is_admin or "QUỸ SHOP" in edit_perms:
                    st.caption("Hủy chứng từ sai sót (Chỉ dành cho Admin/Quản lý Quỹ):")
                    c_sel, c_del = st.columns([3, 1])
                    xoa_id = c_sel.selectbox("Chọn mã chứng từ hủy:", [tx["Mã CT"] for tx in quy_list], label_visibility="collapsed")
                    if c_del.button("❌ HỦY CHỨNG TỪ", type="primary", use_container_width=True):
                        full_id = [tid for tid in qs.keys() if tid[-4:] == xoa_id[-4:]][0]
                        delete_firebase(f"quy_shop/{full_id}")
                        st.success("Đã xóa bỏ chứng từ khỏi sổ gốc!"); time.sleep(0.5); st.rerun()

        # ==========================================
        # 5. TAB ADMIN (MỚI: PHÂN QUYỀN VIEW VÀ EDIT ĐỘC LẬP)
        # ==========================================
        elif selected_tab == "👥 QUẢN TRỊ ADMIN":
            st.markdown("<h3 style='margin-top: 0px; margin-bottom: 25px; font-weight:800;'>⚙️ Trung Tâm Điều Hành Quản Trị Hệ Thống</h3>", unsafe_allow_html=True)
            
            st.markdown("#### ⏳ Yêu Cầu Cấp Tài Khoản Mới Chờ Duyệt")
            pending = db.get("pending_users", {})
            if not pending: st.info("Hiện không có nhân sự nào đang chờ duyệt đăng ký.")
            else:
                for pu, pinfo in pending.items():
                    with st.container():
                        c1, c2, c3 = st.columns([4, 2, 2])
                        c1.markdown(f"**👤 Tài khoản: {pu}**")
                        if c2.button("✅ Phê duyệt cấp quyền", key=f"ok_{pu}", type="primary", use_container_width=True):
                            update_firebase(f"users/{pu}", {"pass": pinfo["pass"], "role": "user", "permissions": ["XEM LỊCH", "TÍCH LŨY", "LỊCH ECOM", "THỊ TRƯỜNG"]})
                            delete_firebase(f"pending_users/{pu}"); st.rerun()
                        if c3.button("❌ Bác bỏ", key=f"rej_{pu}", use_container_width=True):
                            delete_firebase(f"pending_users/{pu}"); st.rerun()
            
            st.divider()
            # BẢNG PHÂN QUYỀN 2 LỚP SIÊU CHI TIẾT
            st.markdown("#### 🔑 Phân Quyền Hạn Tùy Chỉnh (Xem & Sửa) Cho Từng Nhân Sự")
            users = db.get("users", {})
            for u, uinfo in users.items():
                if uinfo.get("role") != "admin":
                    with st.expander(f"👤 Cấu hình quyền cho: {u}"):
                        current_perms = uinfo.get("permissions", [])
                        current_edits = uinfo.get("edit_permissions", [])
                        
                        st.markdown("**1. Cấp quyền XEM (Chỉ được mở đọc dữ liệu):**")
                        new_perms = st.multiselect("Bật/tắt các Tab hiển thị trên điện thoại:", 
                            ["TÍCH LŨY", "XEM LỊCH", "LỊCH ECOM", "THỊ TRƯỜNG", "QUỸ SHOP", "XUẤT EXCEL", "GỬI ZALO"], 
                            default=[p for p in current_perms if p in ["TÍCH LŨY", "XEM LỊCH", "LỊCH ECOM", "THỊ TRƯỜNG", "QUỸ SHOP", "XUẤT EXCEL", "GỬI ZALO"]],
                            key=f"perm_{u}"
                        )
                        
                        st.markdown("**2. Cấp quyền CHỈNH SỬA (Được phép Up Ảnh, Sửa Số, Ghi Sổ...):**")
                        new_edits = st.multiselect("Bật/tắt quyền thao tác trực tiếp:", 
                            ["TÍCH LŨY", "XEM LỊCH", "LỊCH ECOM", "THỊ TRƯỜNG", "QUỸ SHOP"], 
                            default=[p for p in current_edits if p in ["TÍCH LŨY", "XEM LỊCH", "LỊCH ECOM", "THỊ TRƯỜNG", "QUỸ SHOP"]],
                            key=f"edit_{u}"
                        )
                        
                        if st.button("💾 LƯU BẢNG PHÂN QUYỀN NÀY", key=f"save_{u}", type="primary", use_container_width=True):
                            update_firebase(f"users/{u}/permissions", new_perms)
                            update_firebase(f"users/{u}/edit_permissions", new_edits)
                            st.success(f"Đã cập nhật bảng phân quyền chi tiết cho tài khoản {u}!"); time.sleep(0.5); st.rerun()
