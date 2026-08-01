import streamlit as st
import base64

def render_schedule():
    st.markdown("""
    <div class='html-card'>
        <h3 class='html-title' style='text-align: left;'>📋 LỊCH TRỰC TUẦN</h3>
        <p class='html-text' style='text-align: left; margin-bottom: 0px;'>Ảnh lịch trực mới nhất được phân bổ từ Quản lý</p>
    </div>
    """, unsafe_allow_html=True)

    shop_id = st.session_state.get("current_shop", "Shop Chính (Mặc định)")
    
    # 1. Trỏ đúng vào Ngăn Tủ chứa ảnh ("schedule_images")
    if shop_id == "Shop Chính (Mặc định)":
        schedule_data = st.session_state.db.get("schedule_images", {})
    else:
        schedule_data = st.session_state.db.get("shops", {}).get(shop_id, {}).get("schedule_images", {})

    # 2. Xử lý hiển thị
    if not schedule_data:
        st.info("📌 Hiện tại Quản lý chưa tải lên ảnh lịch trực nào cho chi nhánh này.")
        return

    # Nếu có nhiều ảnh, sắp xếp để lấy ảnh mới nhất lên đầu
    try:
        sorted_keys = sorted(schedule_data.keys(), reverse=True)
        
        for key in sorted_keys:
            base64_str = schedule_data[key]
            
            # Xóa các tiền tố bừa bãi nếu có (VD: data:image/jpeg;base64,...)
            if "," in base64_str:
                base64_str = base64_str.split(",")[1]
                
            # Dịch ngược mã hóa thành ảnh thật
            image_bytes = base64.b64decode(base64_str)
            
            st.image(image_bytes, use_column_width=True, caption="Ảnh Lịch Trực Mới Nhất")
            
            # Chỉ hiển thị 1 ảnh mới nhất thôi, tránh nhân viên bị rối
            break 
            
    except Exception as e:
        st.error(f"⚠️ Lỗi hiển thị ảnh lịch: {e}. Vui lòng kiểm tra lại định dạng ảnh trên App Windows.")
