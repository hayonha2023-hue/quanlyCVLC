import streamlit as st
import requests
import time
import base64

FIREBASE_URL = "https://htcv-5c857-default-rtdb.firebaseio.com/htcv.json"

def save_kpi_to_firebase(kpi_data, shop_id):
    try:
        url = FIREBASE_URL if shop_id == "Shop Chính (Mặc định)" else FIREBASE_URL.replace(".json", f"/shops/{shop_id}.json")
        requests.patch(url, json={"kpi": kpi_data}, timeout=10)
        return True
    except Exception as e:
        st.error(f"Lỗi đồng bộ: {e}")
        return False

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
        <h3 class='html-title' style='text-align: left;'>📈 THEO DÕI & CẬP NHẬT KPI</h3>
        <p class='html-text' style='text-align: left; margin-bottom: 0px;'>Xem tiến độ và đồng bộ số liệu chạy số thời gian thực</p>
    </div>
    """, unsafe_allow_html=True)

    shop_id = st.session_state.get("current_shop", "Shop Chính (Mặc định)")
    db = st.session_state.db if shop_id == "Shop Chính (Mặc định)" else st.session_state.db.get("shops", {}).get(shop_id, {})
    
    tab1, tab2 = st.tabs(["🖼️ BẢNG KPI (ẢNH)", "📊 DỮ LIỆU CHI TIẾT & CẬP NHẬT"])

    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        kpi_images = db.get("kpi_images", [])

        if not kpi_images:
            st.info("📌 Hiện tại Quản lý chưa tải lên ảnh KPI nào.")
        else:
            try:
                base64_str = ""
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

    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        kpi_data = db.get("kpi", {})
        emp_kpi = kpi_data.get("emp", {})
        
        if not emp_kpi:
            st.info("📌 Chưa có dữ liệu KPI nhân viên.")
        else:
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
                
                # SỬA LỖI 1: Tính % thật để hiển thị chữ, và % giới hạn (max 100) để vẽ thanh Progress
                true_percent = (sold / tgt * 100) if tgt > 0 else 0
                bar_percent = min(int(true_percent), 100)
                
                # SỬA LỖI 2: Tính toán lại số Còn nợ / Vượt chỉ tiêu dựa trên số thực tế (Không dùng biến short của app Windows nữa)
                if sold >= tgt:
                    vuot = sold - tgt
                    short_display = f"<span class='stat-val' style='color:#0dcaf0;'>+{vuot:,} (Vượt)</span>"
                else:
                    con_thieu = tgt - sold
                    short_display = f"<span class='stat-val' style='color:#dc3545;'>{con_thieu:,}</span>"
                
                medal = "🥇" if idx == 0 else "🥈" if idx == 1 else "🥉" if idx == 2 else "👤"
                
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class='kpi-box'>
                        <div class='kpi-name'>{medal} {name}</div>
                        <div class='stat-row'><span>Chỉ tiêu:</span> <span class='stat-val' style='color:#6c757d;'>{tgt:,}</span></div>
                        <div class='stat-row'><span>Đã đạt:</span> <span class='stat-val' style='color:#198754;'>{sold:,}</span></div>
                        <div class='stat-row'><span>Còn thiếu:</span> {short_display}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    # Hiển thị % thật cho người dùng, vẽ thanh max 100
                    st.progress(bar_percent, text=f"Hoàn thành: {true_percent:.1f}%")
                idx += 1

            st.markdown("<hr>", unsafe_allow_html=True)
            
            if st.session_state.current_user == "admin":
                st.markdown("#### 🔄 CẬP NHẬT SỐ LIỆU KPI (Quyền Admin)")
                
                danh_sach_nv = list(emp_kpi.keys())
                nv_chon = st.selectbox("👤 Chọn nhân viên cần cập nhật:", danh_sach_nv)
                
                current_sold = int(emp_kpi[nv_chon].get("sold", 0)) if nv_chon else 0
                current_tgt = int(emp_kpi[nv_chon].get("tgt", 0)) if nv_chon else 0
                
                with st.form("update_kpi_form"):
                    c1, c2 = st.columns(2)
                    with c1:
                        new_sold = st.number_input("📈 Số Đã Đạt mới (Sold)", min_value=0, value=current_sold, step=1)
                    with c2:
                        new_tgt = st.number_input("🎯 Chỉ Tiêu (Target)", min_value=0, value=current_tgt, step=1)
                        
                    submit_kpi = st.form_submit_button("💾 LƯU & ĐỒNG BỘ LÊN CLOUD", type="primary", use_container_width=True)
                    
                    if submit_kpi:
                        # Giữ nguyên cấu trúc logic tính short (Target - Base) để tránh lỗi với app Windows
                        base = int(emp_kpi[nv_chon].get("base", 0))
                        
                        emp_kpi[nv_chon]["sold"] = new_sold
                        emp_kpi[nv_chon]["tgt"] = new_tgt
                        emp_kpi[nv_chon]["short"] = new_tgt - base
                        
                        kpi_data["emp"] = emp_kpi
                        
                        if shop_id == "Shop Chính (Mặc định)":
                            st.session_state.db["kpi"] = kpi_data
                        else:
                            if "shops" not in st.session_state.db: st.session_state.db["shops"] = {}
                            if shop_id not in st.session_state.db["shops"]: st.session_state.db["shops"][shop_id] = {}
                            st.session_state.db["shops"][shop_id]["kpi"] = kpi_data
                            
                        if save_kpi_to_firebase(kpi_data, shop_id):
                            st.success(f"✅ Đã cập nhật thành công KPI của {nv_chon}!")
                            time.sleep(1.5)
                            st.rerun()
            else:
                st.info("🔒 Bạn đang ở chế độ Chỉ Xem (Read-only). Việc cập nhật số liệu do Quản lý thực hiện trên hệ thống Windows hoặc bằng tài khoản Admin.")
