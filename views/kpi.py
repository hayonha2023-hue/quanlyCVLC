import streamlit as st
import base64

def render_kpi():
    st.markdown("""
    <style>
        .kpi-box { background-color: #fff; padding: 15px; border-radius: 10px; border: 1px solid #e9ecef; box-shadow: 2px 2px 8px rgba(0,0,0,0.03); margin-bottom: 15px; }
        .kpi-name { font-size: 16px; font-weight: bold; color: #0d6efd; text-transform: uppercase; margin-bottom: 5px; }
        .stat-row { display: flex; justify-content: space-between; font-size: 14px; margin-bottom: 3px; }
        .stat-val { font-weight: bold; }
        .img-container { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border: 1px solid #ddd; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='html-card'>
        <h3 class='html-title' style='text-align: left;'>📈 THEO DÕI KPI & MỤC TIÊU</h3>
        <p class='html-text' style='text-align: left; margin-bottom: 0px;'>Ảnh bảng KPI và Dữ liệu chi tiết</p>
    </div>
    """, unsafe_allow_html=True)

    shop_id = st.session_state.get("current_shop", "Shop Chính (Mặc định)")
    db = st.session_state.db if shop_id == "Shop Chính (Mặc định)" else st.session_state.db.get("shops", {}).get(shop_id, {})
    
    # Chia 2 Tab để ưu tiên hiển thị Ảnh
    tab1, tab2 = st.tabs(["🖼️ BẢNG KPI (ẢNH)", "📊 SỐ LIỆU CHI TIẾT"])

    # ==========================================
    # TAB 1: HIỂN THỊ ẢNH KPI TẢI LÊN TỪ WINDOWS
    # ==========================================
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        kpi_images = db.get("kpi_images", [])

        if not kpi_images:
            st.info("📌 Hiện tại Quản lý chưa tải lên ảnh KPI nào.")
        else:
            try:
                base64_str = ""
                # Xử lý cả 2 định dạng List và Dict như đã làm với Lịch trực
                if isinstance(kpi_images, list):
                    valid_images = [img for img in kpi_images if img]
                    if valid_images: base64_str = valid_images[-1]
                elif isinstance(kpi_images, dict):
                    sorted_keys = sorted(kpi_images.keys(), reverse=True)
                    if sorted_keys: base64_str = kpi_images[sorted_keys[0]]

                if base64_str:
                    if "," in base64_str:
                        base64_str = base64_str.split(",")[1]
                    image_bytes = base64.b64decode(base64_str)
                    
                    st.markdown("<div class='img-container'>", unsafe_allow_html=True)
                    st.image(image_bytes, use_container_width=True, caption="Ảnh KPI Mới Nhất")
                    st.markdown("</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"⚠️ Lỗi hiển thị ảnh KPI: {e}")

    # ==========================================
    # TAB 2: DỮ LIỆU SỐ BẰNG CHỮ (Lưu trữ để đối chiếu)
    # ==========================================
    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        kpi_data = db.get("kpi", {})
        emp_kpi = kpi_data.get("emp", {})
        
        if not emp_kpi:
            st.info("📌 Chưa có dữ liệu KPI nhân viên.")
        else:
            # Thuật toán lọc Top những người bán được nhiều nhất lên đầu
            sorted_emps = sorted(
                [(name, data) for name, data in emp_kpi.items() if isinstance(data, dict) and "tgt" in data],
                key=lambda x: int(x[1].get("sold", 0)), 
                reverse=True
            )
            
            cols = st.columns(3)
            idx = 0
            
            for name, data in sorted_emps:
                tgt = int(data.get("tgt", 0))
                sold = int(data.get("sold", 0))
                short = int(data.get("short", 0))
                percent = min((sold / tgt * 100) if tgt > 0 else 0, 100)
                medal = "🥇" if idx == 0 else "🥈" if idx == 1 else "🥉" if idx == 2 else "👤"
                
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class='kpi-box'>
                        <div class='kpi-name'>{medal} {name}</div>
                        <div class='stat-row'><span>Chỉ tiêu:</span> <span class='stat-val' style='color:#6c757d;'>{tgt:,}</span></div>
                        <div class='stat-row'><span>Đã đạt:</span> <span class='stat-val' style='color:#198754;'>{sold:,}</span></div>
                        <div class='stat-row'><span>Còn thiếu:</span> <span class='stat-val' style='color:#dc3545;'>{short:,}</span></div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.progress(int(percent), text=f"Hoàn thành: {percent:.1f}%")
                idx += 1
