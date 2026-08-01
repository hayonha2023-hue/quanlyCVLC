import streamlit as st
import base64

TEXT_SCHEDULE_KEY = "detailed_history" 

def render_schedule():
    # 1. NHÚNG CSS ĐỂ TRANG WEB "LỘT XÁC"
    st.markdown("""
    <style>
        /* Tùy chỉnh thẻ Card chứa lịch */
        .schedule-card {
            background-color: #ffffff;
            border-left: 6px solid #0d6efd;
            border-radius: 10px;
            padding: 15px 20px;
            margin-bottom: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            border: 1px solid #f0f0f0;
            transition: transform 0.2s;
        }
        .schedule-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.1);
        }
        /* Tùy chỉnh tiêu đề ngày */
        .day-title {
            color: #0d6efd;
            font-weight: 800;
            font-size: 16px;
            margin-bottom: 12px;
            border-bottom: 2px dashed #e9ecef;
            padding-bottom: 8px;
            text-transform: uppercase;
        }
        /* Tùy chỉnh dòng ca trực */
        .shift-row {
            font-size: 15px;
            color: #495057;
            margin-bottom: 8px;
            line-height: 1.5;
        }
        /* Khung chứa ảnh */
        .img-container {
            background: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border: 1px solid #ddd;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='html-card'>
        <h3 class='html-title' style='text-align: left;'>📋 LỊCH TRỰC TUẦN</h3>
        <p class='html-text' style='text-align: left; margin-bottom: 0px;'>Xem phân bổ ca trực chi tiết của toàn bộ chi nhánh</p>
    </div>
    """, unsafe_allow_html=True)

    shop_id = st.session_state.get("current_shop", "Shop Chính (Mặc định)")
    
    # 2. CHIA TAB (THẺ) ĐỂ GIAO DIỆN GỌN GÀNG
    tab1, tab2 = st.tabs(["📅 BẢNG CA TRỰC (CHỮ)", "🖼️ ẢNH LỊCH TỔNG HỢP"])

    # ==========================================
    # TAB 1: HIỂN THỊ CA TRỰC DẠNG CARD (LƯỚI)
    # ==========================================
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        if shop_id == "Shop Chính (Mặc định)":
            schedule_text = st.session_state.db.get(TEXT_SCHEDULE_KEY, {})
        else:
            schedule_text = st.session_state.db.get("shops", {}).get(shop_id, {}).get(TEXT_SCHEDULE_KEY, {})

        if not schedule_text:
            st.info("📌 Hệ thống đang trống lịch trực tuần này.")
        else:
            if isinstance(schedule_text, dict):
                # Chia màn hình thành 2 cột ngang cho cân đối
                cols = st.columns(2)
                idx = 0
                
                for day, ca_truc in schedule_text.items():
                    col = cols[idx % 2] # Luân phiên nhét dữ liệu vào cột Trái - Phải
                    with col:
                        html_content = f"<div class='schedule-card'><div class='day-title'>📅 {day}</div>"
                        
                        if isinstance(ca_truc, dict):
                            for ca, nhan_vien in ca_truc.items():
                                nhan_vien_str = ", ".join(nhan_vien) if isinstance(nhan_vien, list) else str(nhan_vien)
                                
                                # Đổ màu chữ phân biệt Sáng/Chiều cho sang
                                color = "#198754" if "Sáng" in ca else "#fd7e14" if "Chiều" in ca else "#6c757d"
                                icon = "🌅" if "Sáng" in ca else "🌇" if "Chiều" in ca else "🔹"
                                
                                html_content += f"<div class='shift-row'>{icon} <span style='color: {color}; font-weight: bold;'>Ca {ca}:</span> <b>{nhan_vien_str}</b></div>"
                        else:
                            html_content += f"<div class='shift-row'>{ca_truc}</div>"
                            
                        html_content += "</div>"
                        st.markdown(html_content, unsafe_allow_html=True)
                    idx += 1

    # ==========================================
    # TAB 2: HIỂN THỊ ẢNH (CÓ KHUNG VIỀN ĐỔ BÓNG)
    # ==========================================
    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        if shop_id == "Shop Chính (Mặc định)":
            schedule_images = st.session_state.db.get("schedule_images", [])
        else:
            schedule_images = st.session_state.db.get("shops", {}).get(shop_id, {}).get("schedule_images", [])

        if not schedule_images:
            st.info("📌 Hiện tại Quản lý chưa tải lên ảnh lịch trực nào.")
        else:
            try:
                base64_str = ""
                if isinstance(schedule_images, list):
                    valid_images = [img for img in schedule_images if img]
                    if valid_images: base64_str = valid_images[-1]
                elif isinstance(schedule_images, dict):
                    sorted_keys = sorted(schedule_images.keys(), reverse=True)
                    if sorted_keys: base64_str = schedule_images[sorted_keys[0]]

                if base64_str:
                    if "," in base64_str:
                        base64_str = base64_str.split(",")[1]
                    image_bytes = base64.b64decode(base64_str)
                    
                    # Cho ảnh vào khung đổ bóng xịn xò
                    st.markdown("<div class='img-container'>", unsafe_allow_html=True)
                    st.image(image_bytes, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"⚠️ Lỗi hiển thị ảnh lịch: {e}")
