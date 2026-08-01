import streamlit as st
import pandas as pd
import requests
import time

FIREBASE_URL = "https://htcv-5c857-default-rtdb.firebaseio.com/htcv.json"

def update_firebase_market(path, data, shop_id):
    db_path = path if shop_id == "Shop Chính (Mặc định)" else f"shops/{shop_id}/{path}"
    try:
        requests.patch(f"{FIREBASE_URL.replace('.json', '')}/{db_path}.json", json=data)
    except Exception as e:
        st.error(f"Lỗi: {e}")

def render_market():
    st.markdown("<h3 style='margin-top: 0px; margin-bottom: 25px; font-weight:800;'>📍 Bản Đồ Phân Công Công Tác Thị Trường</h3>", unsafe_allow_html=True)
    
    shop_id = st.session_state.get("current_shop", "Shop Chính (Mặc định)")
    full_db = st.session_state.get("db", {})
    db = full_db if shop_id == "Shop Chính (Mặc định)" else full_db.get("shops", {}).get(shop_id, {})
    
    market_data = db.get("market_history", {})
    
    # BỌC THÉP KIỂM TRA QUYỀN ADMIN (Bắt chuẩn mọi tài khoản Quản lý)
    current_user = st.session_state.get("user", "")
    is_sys_admin = st.session_state.get("is_admin", False)
    is_sys_super = st.session_state.get("is_super_admin", False)
    u_info = full_db.get("users", {}).get(current_user, {})
    user_role = u_info.get("role", "")
    edit_perms = u_info.get("edit_permissions", [])
    
    can_edit = (is_sys_admin) or (is_sys_super) or (current_user == "admin") or (user_role == "admin") or ("SỬA THỊ TRƯỜNG" in edit_perms)

    # NẾU LÀ ADMIN -> HIỆN FORM THÊM LỊCH
    if can_edit:
        with st.expander("➕ THÊM / SỬA LỊCH THỊ TRƯỜNG (Quyền Admin)", expanded=False):
            with st.form("market_form"):
                c1, c2 = st.columns(2)
                m_date = c1.date_input("Kế hoạch Ngày")
                m_loc = c2.text_input("📍 Địa Điểm (Tuyến)", placeholder="VD: Huyện A, Tỉnh B...")
                
                # Tự động lấy danh sách nhân sự từ KPI để cho vào menu chọn
                kpi_emp = db.get("kpi", {}).get("emp", {})
                danh_sach_nv = list(kpi_emp.keys()) if kpi_emp else ["An", "Hoàng", "Lan", "Hương", "Duyên", "Đạt", "Ngọc", "Dịu", "Huyền", "Nhài"]
                
                m_emps = st.multiselect("👥 Chọn Nhân viên đi tuyến:", danh_sach_nv)
                
                submit_market = st.form_submit_button("💾 LƯU LỊCH THỊ TRƯỜNG", type="primary", use_container_width=True)
                
                if submit_market:
                    if m_loc and m_emps:
                        # Firebase không cho lưu Key có chứa dấu "/", nên ta chuyển thành dấu "-"
                        date_key = m_date.strftime("%d-%m-%Y") 
                        new_data = {
                            "dia_diem": m_loc,
                            "nhan_vien": m_emps
                        }
                        update_firebase_market(f"market_history/{date_key}", new_data, shop_id)
                        
                        # Cập nhật RAM để hiển thị liền
                        if "market_history" not in db: db["market_history"] = {}
                        db["market_history"][date_key] = new_data
                        
                        st.success(f"✅ Đã lưu lịch công tác ngày {m_date.strftime('%d/%m/%Y')}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Vui lòng nhập địa điểm và chọn ít nhất 1 nhân viên!")

    st.markdown("<hr style='margin-top:5px; margin-bottom:20px;'>", unsafe_allow_html=True)
    
    # HIỂN THỊ BẢNG LỊCH CHO NHÂN VIÊN XEM
    if not market_data:
        st.info("📌 Chưa có lịch phân công tác thị trường.")
    else:
        market_list = []
        for d, inf in market_data.items():
            display_date = d.replace("-", "/") # Đổi ngược lại thành dấu / cho đẹp mắt
            market_list.append({
                "Kế hoạch Ngày": display_date, 
                "📍 Địa Điểm": inf.get("dia_diem", ""), 
                "👥 Tuyến": ", ".join(inf.get("nhan_vien", [])) if isinstance(inf.get("nhan_vien"), list) else inf.get("nhan_vien", "")
            })
        
        st.dataframe(pd.DataFrame(market_list), hide_index=True, use_container_width=True)
        
        # Admin được quyền Hủy lịch
        if can_edit:
            c_del1, c_del2 = st.columns([3, 1])
            del_date = c_del1.selectbox("Chọn ngày để xóa lịch:", list(market_data.keys()), format_func=lambda x: x.replace("-", "/"), label_visibility="collapsed")
            if c_del2.button("❌ HỦY LỊCH NÀY", type="primary", use_container_width=True):
                db_path = f"market_history/{del_date}" if shop_id == "Shop Chính (Mặc định)" else f"shops/{shop_id}/market_history/{del_date}"
                requests.delete(f"{FIREBASE_URL.replace('.json', '')}/{db_path}.json")
                st.success("✅ Đã xóa lịch thành công!")
                time.sleep(1)
                st.rerun()
