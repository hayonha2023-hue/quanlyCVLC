from services.database import save, shop_path
import streamlit as st
import requests
import time
from views.workspace import page_header, sync_status

# Đường dẫn DB của bạn
FIREBASE_URL = "https://htcv-5c857-default-rtdb.firebaseio.com/htcv.json"

def save_ecom_to_firebase(ecom_data, shop_id):
    return save(shop_path(shop_id), {'ecom_history': ecom_data})

def render_ecom():
    sync_status()
    page_header('Chỉnh sửa lịch Ecom', 'Phân công nhân viên theo ca sáng và ca chiều trong tuần.', 'CHỈNH SỬA DỮ LIỆU')

    # Lấy ID của Chi nhánh hiện tại
    shop_id = st.session_state.get("current_shop", "Shop Chính (Mặc định)")

    # Lôi dữ liệu cũ từ trong bộ nhớ tạm ra
    if shop_id == "Shop Chính (Mặc định)":
        ecom_history = st.session_state.db.get("ecom_history", {})
    else:
        ecom_history = st.session_state.db.get("shops", {}).get(shop_id, {}).get("ecom_history", {})

    user = st.session_state.get('user', '')
    account = st.session_state.db.get('users', {}).get(user, {})
    can_edit = st.session_state.get('is_admin', False) or 'SỬA LỊCH ECOM' in account.get('edit_permissions', [])
    days = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"]

    # Tạo Form nhập liệu
    with st.form("ecom_form"):
        inputs = {}
        for d in days:
            st.markdown(f"**{d}**")
            col1, col2 = st.columns(2)

            # Lấy dữ liệu cũ để điền sẵn vào ô
            old_val = ecom_history.get(d, {})
            old_s = old_val.get("Sáng", "") if isinstance(old_val, dict) else old_val
            old_c = old_val.get("Chiều", "") if isinstance(old_val, dict) else ""

            with col1:
                s_val = st.text_input("Ca sáng", value=old_s, key=f"ecom_{shop_id}_s_{d}", disabled=not can_edit)
            with col2:
                c_val = st.text_input("Ca chiều", value=old_c, key=f"ecom_{shop_id}_c_{d}", disabled=not can_edit)

            inputs[d] = {"Sáng": s_val.strip(), "Chiều": c_val.strip()}
            st.divider()

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            submitted = st.form_submit_button("Lưu lịch Ecom", disabled=not can_edit, type="primary", use_container_width=True)
        with col_btn2:
            swap_btn = st.form_submit_button("Đảo ca sáng / chiều", disabled=not can_edit, use_container_width=True)

        # Xử lý nút LƯU
        if submitted:
            # Bắn lên Mây
            if save_ecom_to_firebase(inputs, shop_id):
                st.success("✅ Đã lưu và đồng bộ Lịch Ecom lên hệ thống!")
                time.sleep(1.5)
                st.rerun()

        # Xử lý nút ĐẢO CA
        if swap_btn:
            swapped_inputs = {}
            for d in days:
                swapped_inputs[d] = {
                    "Sáng": inputs[d]["Chiều"],
                    "Chiều": inputs[d]["Sáng"]
                }

            # Bắn lên Mây
            if save_ecom_to_firebase(swapped_inputs, shop_id):
                st.success("✅ Đã đảo ca Sáng/Chiều thành công!")
                time.sleep(1.5)
                st.rerun()
