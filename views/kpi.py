import streamlit as st

def render_kpi():
    st.markdown("""
    <style>
        .kpi-box { background-color: #fff; padding: 15px; border-radius: 10px; border: 1px solid #e9ecef; box-shadow: 2px 2px 8px rgba(0,0,0,0.03); margin-bottom: 15px; }
        .kpi-name { font-size: 16px; font-weight: bold; color: #0d6efd; text-transform: uppercase; margin-bottom: 5px; }
        .stat-row { display: flex; justify-content: space-between; font-size: 14px; margin-bottom: 3px; }
        .stat-val { font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='html-card'>
        <h3 class='html-title' style='text-align: left;'>📈 THEO DÕI KPI & MỤC TIÊU</h3>
        <p class='html-text' style='text-align: left; margin-bottom: 0px;'>Bảng vàng thành tích và tiến độ chạy số của chi nhánh</p>
    </div>
    """, unsafe_allow_html=True)

    shop_id = st.session_state.get("current_shop", "Shop Chính (Mặc định)")
    db = st.session_state.db if shop_id == "Shop Chính (Mặc định)" else st.session_state.db.get("shops", {}).get(shop_id, {})
    
    # Lấy dữ liệu KPI
    kpi_data = db.get("kpi", {})
    emp_kpi = kpi_data.get("emp", {})
    thang = kpi_data.get("m", "")
    
    # Chia 2 Tab: Cá nhân & Tổng quan
    tab1, tab2 = st.tabs(["🎯 KPI CÁ NHÂN", "🏆 MỤC TIÊU CHUNG SHOP"])

    # ==========================================
    # TAB 1: KPI TỪNG NHÂN VIÊN
    # ==========================================
    with tab1:
        st.markdown(f"#### 🏆 BẢNG THÀNH TÍCH THÁNG {thang}")
        if not emp_kpi:
            st.info("📌 Chưa có dữ liệu KPI nhân viên tháng này.")
        else:
            # Sắp xếp nhân viên có số "Đã đạt (sold)" cao nhất lên đầu (Bảng vàng)
            sorted_emps = sorted(
                [(name, data) for name, data in emp_kpi.items() if isinstance(data, dict) and "tgt" in data],
                key=lambda x: x[1].get("sold", 0), 
                reverse=True
            )
            
            cols = st.columns(3) # Chia 3 cột cho đẹp
            idx = 0
            
            for name, data in sorted_emps:
                tgt = int(data.get("tgt", 0))
                sold = int(data.get("sold", 0))
                short = int(data.get("short", 0))
                
                # Tính % hoàn thành
                percent = (sold / tgt * 100) if tgt > 0 else 0
                percent = min(percent, 100) # Tối đa 100% cho thanh Progress bar
                
                # Huy chương cho Top 3
                medal = "🥇" if idx == 0 else "🥈" if idx == 1 else "🥉" if idx == 2 else "👤"
                
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class='kpi-box'>
                        <div class='kpi-name'>{medal} {name}</div>
                        <div class='stat-row'><span>Chỉ tiêu (Target):</span> <span class='stat-val' style='color:#6c757d;'>{tgt:,}</span></div>
                        <div class='stat-row'><span>Đã đạt (Sold):</span> <span class='stat-val' style='color:#198754;'>{sold:,}</span></div>
                        <div class='stat-row'><span>Còn thiếu (Short):</span> <span class='stat-val' style='color:#dc3545;'>{short:,}</span></div>
                    </div>
                    """, unsafe_allow_html=True)
                    # Thanh tiến độ
                    st.progress(int(percent), text=f"Hoàn thành: {percent:.1f}%")
                idx += 1

    # ==========================================
    # TAB 2: MỤC TIÊU CHUNG CỦA SHOP
    # ==========================================
    with tab2:
        st.markdown("#### 🎯 CHỈ SỐ HOẠT ĐỘNG (DAILY TARGETS)")
        daily_targets = db.get("daily_targets", {}).get("metrics", {})
        
        if not daily_targets:
            st.info("📌 Chưa có dữ liệu mục tiêu chung.")
        else:
            cols = st.columns(4)
            idx = 0
            for metric_name, metric_data in daily_targets.items():
                if isinstance(metric_data, dict):
                    # Lấy các chỉ số từ JSON (VD: g, p...)
                    g_val = metric_data.get("g", "0")
                    p_val = metric_data.get("p", "0")
                    
                    with cols[idx % 4]:
                        # Dùng thẻ Metric của Streamlit để tạo các khối số liệu đẹp
                        st.metric(label=metric_name, value=g_val, delta=f"Target: {p_val}", delta_color="normal")
                    idx += 1
