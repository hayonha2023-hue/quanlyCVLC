import streamlit as st
import requests
import time

FIREBASE_URL = "https://htcv-5c857-default-rtdb.firebaseio.com/htcv.json"

def update_firebase_global(path, data):
    try: requests.patch(f"{FIREBASE_URL.replace('.json', '')}/{path}.json", json=data)
    except Exception as e: st.error(f"Lỗi đồng bộ: {e}")

def delete_firebase_global(path):
    try: requests.delete(f"{FIREBASE_URL.replace('.json', '')}/{path}.json")
    except Exception as e: st.error(f"Lỗi đồng bộ: {e}")

def render_admin():
    st.markdown("<h3 style='margin-top: 0px; margin-bottom: 25px; font-weight:800;'>⚙️ Trung Tâm Điều Hành Quản Trị Hệ Thống</h3>", unsafe_allow_html=True)
    
    full_db = st.session_state.get("db", {})
    current_shop = st.session_state.get("current_shop", "Shop Chính (Mặc định)")
    
    is_super_admin = st.session_state.get("is_super_admin", False)
    is_admin = st.session_state.get("is_admin", False)
    
    # Chỉ Admin mới được vào xem trang này
    if not (is_super_admin or is_admin):
        st.warning("⛔ Bạn không có quyền truy cập khu vực này!")
        return

    # ==========================================
    # 1. DANH SÁCH DUYỆT TÀI KHOẢN MỚI
    # ==========================================
    pending = full_db.get("pending_users", {})
    if pending:
        st.markdown("<h5 style='color:#f59e0b; font-weight: bold;'>⏳ TÀI KHOẢN CHỜ PHÊ DUYỆT</h5>", unsafe_allow_html=True)
        for pu, pinfo in pending.items():
            req_shop = pinfo.get("shop_id", "Shop Chính (Mặc định)") if isinstance(pinfo, dict) else "Shop Chính (Mặc định)"
            
            # Chúa tể duyệt hết, Admin nhánh chỉ duyệt người xin vào nhánh mình
            if is_super_admin or req_shop == current_shop:
                with st.container():
                    c1, c2, c3 = st.columns([4, 2, 2])
                    c1.markdown(f"**👤 Tên Đăng Nhập:** `{pu}` (📍 {req_shop})")
                    if c2.button("✅ Phê duyệt", key=f"ok_{pu}", type="primary", use_container_width=True):
                        pwd = pinfo.get("pass", "123456") if isinstance(pinfo, dict) else pinfo
                        
                        # Cấp quyền mặc định khi mới duyệt
                        update_firebase_global(f"users/{pu}", {
                            "pass": pwd, 
                            "role": "user", 
                            "shop_id": req_shop, 
                            "permissions": ["XEM LỊCH", "TÍCH LŨY"], 
                            "edit_permissions": []
                        })
                        delete_firebase_global(f"pending_users/{pu}")
                        st.success(f"Đã duyệt tài khoản {pu}!"); time.sleep(1); st.rerun()
                        
                    if c3.button("❌ Bác bỏ", key=f"rej_{pu}", use_container_width=True):
                        delete_firebase_global(f"pending_users/{pu}")
                        st.warning(f"Đã từ chối tài khoản {pu}!"); time.sleep(1); st.rerun()
        st.divider()

    # ==========================================
    # 2. QUẢN LÝ TÀI KHOẢN NHÂN VIÊN ĐÃ DUYỆT
    # ==========================================
    st.markdown("<h5 style='color:#10b981; font-weight: bold;'>👥 QUẢN LÝ NHÂN SỰ & PHÂN QUYỀN</h5>", unsafe_allow_html=True)
    
    global_users = full_db.get("users", {})
    shops_data = full_db.get("shops", {})
    all_shops = ["Shop Chính (Mặc định)"] + list(shops_data.keys())
    
    for u, uinfo in global_users.items():
        # Bỏ qua tài khoản Chúa tể tối cao, không ai được sửa
        if u == "admin": continue
        
        u_shop = uinfo.get("shop_id", "Shop Chính (Mặc định)")
        u_role = uinfo.get("role", "user")
        
        # Điều kiện hiển thị: 
        # - Super Admin thấy tất cả.
        # - Admin nhánh chỉ thấy nhân viên nhánh mình (và không được sửa quyền của Admin nhánh khác/cùng nhánh).
        if is_super_admin or (u_shop == current_shop and u_role != "admin"):
            with st.expander(f"👤 {u} (Vai trò: {u_role.upper()} | 📍 {u_shop})"):
                
                new_shop = u_shop
                new_role = u_role
                
                # Chỉ Super Admin mới được điều chuyển Shop và nâng/hạ cấp Admin
                if is_super_admin:
                    col_s1, col_s2 = st.columns(2)
                    new_shop = col_s1.selectbox("🏢 Điều chuyển Shop:", all_shops, index=all_shops.index(u_shop) if u_shop in all_shops else 0, key=f"shop_{u}")
                    new_role = col_s2.selectbox("👑 Cấp bậc:", ["user", "admin"], index=0 if u_role=="user" else 1, key=f"role_{u}")
                
                current_perms = uinfo.get("permissions", [])
                current_edits = uinfo.get("edit_permissions", [])
                
                # Danh sách quyền y hệt bản gốc
                view_options = ["XEM LỊCH", "TÍCH LŨY", "QUÉT AI KPI", "CHIA TARGET", "CHIA DATA", "THỊ TRƯỜNG", "HOÀN TÁC", "DANH BẠ", "LẬP HÀNG", "XUẤT EXCEL", "GỬI ZALO", "QUỸ SHOP", "LỊCH ECOM", "AI TƯ VẤN"]
                new_perms = st.multiselect("Bật/tắt các tính năng xem:", view_options, default=[p for p in current_perms if p in view_options], key=f"perm_{u}")
                
                edit_options = ["SỬA SỐ KPI", "UP ẢNH KPI", "CHIA LỊCH TỰ ĐỘNG", "UP ẢNH LỊCH TRỰC", "SỬA LỊCH ECOM", "SỬA THỊ TRƯỜNG", "QUẢN LÝ QUỸ SHOP", "ĐẢO TÊN CA", "TÍNH TARGET"]
                new_edits = st.multiselect("Bật/tắt quyền chỉnh sửa (Thao tác):", edit_options, default=[p for p in current_edits if p in edit_options], key=f"edit_{u}")
                
                if st.button("💾 LƯU CẤU HÌNH TÀI KHOẢN NÀY", key=f"save_{u}", type="primary", use_container_width=True):
                    update_firebase_global(f"users/{u}", {
                        "pass": uinfo.get("pass"), 
                        "bg_image": uinfo.get("bg_image", ""), 
                        "role": new_role, 
                        "shop_id": new_shop, 
                        "permissions": new_perms, 
                        "edit_permissions": new_edits
                    })
                    st.success(f"Đã cập nhật quyền cho {u}!"); time.sleep(1); st.rerun()
