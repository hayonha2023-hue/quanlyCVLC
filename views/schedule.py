import streamlit as st
import base64

# Đã khóa mục tiêu đúng tên ngăn tủ của bạn!
TEXT_SCHEDULE_KEY = "detailed_history" 

def render_schedule():
    st.markdown("""
    <div class='html-card'>
        <h3 class='html-title' style='text-align: left;'>📋 LỊCH TRỰC TUẦN</h3>
        <p class='html-text' style='text-align: left; margin-bottom: 0px;'>Danh sách ca trực và Ảnh lịch phân bổ từ Quản lý</p>
    </div>
    """, unsafe_allow_html=True)

    shop_id = st.session_state.get("current_shop", "Shop Chính (Mặc định)")
    
    # ==========================================
    # PHẦN 1: HIỂN THỊ CA TRỰC BẰNG CHỮ (TEXT)
    # ==========================================
    if shop_id == "Shop Chính (Mặc định)":
        schedule_text = st.session_state.db.get(TEXT_SCHEDULE_KEY, {})
    else:
        schedule_text = st.session_state.db.get("shops", {}).get(shop_id, {}).get(TEXT_SCHEDULE_KEY, {})

    st.markdown("#### 📅 PHÂN BỔ CA TRỰC CHI TIẾT")
    if not schedule_text:
        st.info("📌 Hệ thống đang trống lịch trực tuần này.")
    else:
        if isinstance(schedule_text, dict):
            for day, ca_truc in schedule_text.items():
                # Tạo các thẻ mở rộng cho từng ngày (06-07 - Monday...)
                with st.expander(f"📌 {day}", expanded=True):
                    if isinstance(ca_truc, dict):
                        for ca, nhan_vien in ca_truc.items():
                            # Xóa dấu ngoặc vuông [], ghép tên bằng dấu phẩy cho đẹp
                            if isinstance(nhan_vien, list):
                                nhan_vien_str = ", ".join(nhan_vien)
                            else:
                                nhan_vien_str = str(nhan_vien)
                            st.markdown(f"- **Ca {ca}:** {nhan_vien_str}")
                    else:
                        st.markdown(f"{ca_truc}")
                        
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # ==========================================
    # PHẦN 2: HIỂN THỊ ẢNH LỊCH TẢI LÊN TỪ WINDOWS
    # ==========================================
    st.markdown("#### 🖼️ ẢNH LỊCH TỔNG HỢP")
    if shop_id == "Shop Chính (Mặc định)":
        schedule_images = st.session_state.db.get("schedule_images", [])
    else:
        schedule_images = st.session_state.db.get("shops", {}).get(shop_id, {}).get("schedule_images", [])

    if not schedule_images:
        st.info("📌 Hiện tại Quản lý chưa tải lên ảnh lịch trực nào.")
        return

    try:
        base64_str = ""
        if isinstance(schedule_images, list):
            valid_images = [img for img in schedule_images if img]
            if valid_images:
                base64_str = valid_images[-1]
        elif isinstance(schedule_images, dict):
            sorted_keys = sorted(schedule_images.keys(), reverse=True)
            if sorted_keys:
                base64_str = schedule_images[sorted_keys[0]]

        if not base64_str:
            return

        if "," in base64_str:
            base64_str = base64_str.split(",")[1]
            
        image_bytes = base64.b64decode(base64_str)
        st.image(image_bytes, use_container_width=True, caption="Ảnh Lịch Trực Mới Nhất")
            
    except Exception as e:
        st.error(f"⚠️ Lỗi hiển thị ảnh lịch: {e}")
