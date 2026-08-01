import streamlit as st
import requests
import time

# Đường dẫn DB của bạn
FIREBASE_URL = "https://htcv-5c857-default-rtdb.firebaseio.com/htcv.json"

def save_ecom_to_firebase(ecom_data, shop_id):
    """Bắn dữ liệu Lịch Ecom thẳng lên Firebase"""
    try:
        url = FIREBASE_URL if shop_id == "Shop Chính (Mặc định)" else FIREBASE_URL.replace(".json", f"/shops/{shop_id}.json")
        requests.patch(url, json={"ecom_history": ecom_data}, timeout=10)
        return True
    except Exception as e:
        st.error(f"Lỗi đồng bộ: {e}")
        return False

def render_ecom():
    st.markdown("""
    <div class='html-card'>
        <h3 class='html-title' style='text-align: left;'>🛒 QUẢN LÝ LỊCH ECOM</h3>
        <p class='html-text' style='text-align: left; margin-bottom: 0px;'>Nhập tên nhân viên trực Ecom theo Ca Sáng và Ca Chiều</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Lấy ID của Chi nhánh hiện tại
    shop_id = st.session_state.get("current_shop", "Shop Chính (Mặc định)")
    
    # Lôi dữ liệu cũ từ trong bộ nhớ tạm ra
    if shop_id == "Shop Chính (Mặc định)":
        ecom_history = st.session_state.db.get("ecom_history", {})
    else:
        ecom_history = st.session_state.db.get("shops", {}).get(shop_id, {}).get("ecom_history", {})

    days = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"]
    
    # Tạo Form nhập liệu
    with st.form("ecom_form"):
        inputs = {}
        for d in days:
            st.markdown(f"<p style='color: #0D6EFD; font-weight: bold; margin-bottom: 0px;'>{d}</p>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            
            # Lấy dữ liệu cũ để điền sẵn vào ô
            old_val = ecom_history.get(d, {})
            old_s = old_val.get("Sáng", "") if isinstance(old_val, dict) else old_val
            old_c = old_val.get("Chiều", "") if isinstance(old_val, dict) else ""
            
            with col1:
                s_val = st.text_input("🌅 Sáng:", value=old_s, key=f"s_{d}")
            with col2:
                c_val = st.text_input("🌇 Chiều:", value=old_c, key=f"c_{d}")
            
            inputs[d] = {"Sáng": s_val.strip(), "Chiều": c_val.strip()}
            st.markdown("<hr style='margin-top: 5px; margin-bottom: 15px;'>", unsafe_allow_html=True)
            
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            submitted = st.form_submit_button("💾 LƯU LỊCH ECOM", type="primary", use_container_width=True)
        with col_btn2:
            swap_btn = st.form_submit_button("🔄 ĐẢO CA (SÁNG ⇄ CHIỀU)", use_container_width=True)

        # Xử lý nút LƯU
        if submitted:
            # Cập nhật vào RAM của Web
            if shop_id == "Shop Chính (Mặc định)":
                st.session_state.db["ecom_history"] = inputs
            else:
                if "shops" not in st.session_state.db: st.session_state.db["shops"] = {}
                if shop_id not in st.session_state.db["shops"]: st.session_state.db["shops"][shop_id] = {}
                st.session_state.db["shops"][shop_id]["ecom_history"] = inputs
            
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
            
            # Cập nhật vào RAM của Web
            if shop_id == "Shop Chính (Mặc định)":
                st.session_state.db["ecom_history"] = swapped_inputs
            else:
                st.session_state.db["shops"][shop_id]["ecom_history"] = swapped_inputs
                
            # Bắn lên Mây
            if save_ecom_to_firebase(swapped_inputs, shop_id):
                st.success("✅ Đã đảo ca Sáng/Chiều thành công!")
                time.sleep(1.5)
                st.rerun()
