import streamlit as st
import requests
import time
from datetime import datetime

FIREBASE_URL = "https://htcv-5c857-default-rtdb.firebaseio.com/htcv.json"
DB_KEY = "quy_shop" 

def save_fund_to_firebase(fund_data, shop_id):
    try:
        url = FIREBASE_URL if shop_id == "Shop Chính (Mặc định)" else FIREBASE_URL.replace(".json", f"/shops/{shop_id}.json")
        requests.patch(url, json={DB_KEY: fund_data}, timeout=10)
        return True
    except Exception as e:
        st.error(f"Lỗi đồng bộ: {e}")
        return False

def render_fund():
    st.markdown("<h3 style='color: #0D6EFD; margin-bottom: 20px;'>💰 SỔ QUẢN LÝ THU CHI (QUỸ SHOP)</h3>", unsafe_allow_html=True)

    shop_id = st.session_state.get("current_shop", "Shop Chính (Mặc định)")
    
    # 1. Kéo dữ liệu dạng Từ điển (Dict) chuẩn theo Firebase của bạn
    if shop_id == "Shop Chính (Mặc định)":
        fund_data = st.session_state.db.get(DB_KEY, {})
    else:
        fund_data = st.session_state.db.get("shops", {}).get(shop_id, {}).get(DB_KEY, {})
        
    if not isinstance(fund_data, dict):
        fund_data = {}

    # 2. Tính toán 4 chỉ số (Khớp hoàn toàn form Windows)
    tong_thu = sum([float(item.get("amount", 0)) for item in fund_data.values() if item.get("type") == "Thu"])
    tong_chi = sum([float(item.get("amount", 0)) for item in fund_data.values() if item.get("type") == "Chi"])
    chi_rieng = sum([float(item.get("amount", 0)) for item in fund_data.values() if item.get("type") == "Chi Riêng"])
    ton_quy = tong_thu - tong_chi - chi_rieng 

    # 3. Hiển thị 4 Khối Thống Kê
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f"<div class='html-card' style='text-align:center; padding: 15px;'><b>🏦 TỒN QUỸ</b><br><h3 style='color:#0d6efd; margin-top:5px;'>{ton_quy:,.0f} ₫</h3></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='html-card' style='text-align:center; padding: 15px;'><b>🟢 TỔNG THU</b><br><h3 style='color:#198754; margin-top:5px;'>{tong_thu:,.0f} ₫</h3></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='html-card' style='text-align:center; padding: 15px;'><b>🔴 TỔNG CHI</b><br><h3 style='color:#dc3545; margin-top:5px;'>{tong_chi:,.0f} ₫</h3></div>", unsafe_allow_html=True)
    c4.markdown(f"<div class='html-card' style='text-align:center; padding: 15px;'><b>🟡 CHI RIÊNG</b><br><h3 style='color:#ffc107; margin-top:5px;'>{chi_rieng:,.0f} ₫</h3></div>", unsafe_allow_html=True)

    # 4. Hiển thị Danh sách Giao Dịch
    # Sắp xếp theo ID (chuỗi số thời gian) để cái mới nhất nổi lên đầu
    sorted_funds = sorted(fund_data.items(), key=lambda x: x[0], reverse=True)
    
    for tx_id, item in sorted_funds:
        loai = item.get("type", "")
        color = "#198754" if loai == "Thu" else "#dc3545" if loai == "Chi" else "#ffc107"
        icon = "➕" if loai == "Thu" else "➖"

        st.markdown(f"""
        <div style='background: white; padding: 15px; border-radius: 5px; border: 1px solid #ddd; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;'>
            <div style='width: 15%; color: #666; font-size: 13px;'>{item.get('date', '')}</div>
            <div style='width: 10%; color: {color}; font-weight: bold;'>{icon} {loai}</div>
            <div style='width: 15%; font-weight: bold; font-size: 16px;'>{float(item.get('amount', 0)):,.0f} ₫</div>
            <div style='width: 45%; color: #333;'>{item.get('desc', '')}</div>
            <div style='width: 15%; text-align: right; color: #0d6efd; font-style: italic;'>{item.get('user', '')}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 5. Form nhập liệu Ghi Phiếu (Dàn hàng ngang dưới cùng)
    with st.form("fund_form", clear_on_submit=True):
        st.markdown("<b>GHI PHIẾU MỚI</b>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns([2, 3, 5, 2])
        with col1:
            loai_gd = st.selectbox("Phân Loại", ["Thu", "Chi", "Chi Riêng"], label_visibility="collapsed")
        with col2:
            gia_tri = st.number_input("Giá trị", min_value=0, step=1000, label_visibility="collapsed", placeholder="Nhập số tiền...")
        with col3:
            ly_do = st.text_input("Lý do", label_visibility="collapsed", placeholder="Nội dung...")
        with col4:
            submit = st.form_submit_button("💾 GHI PHIẾU", type="primary", use_container_width=True)

        if submit:
            if gia_tri <= 0 or not ly_do:
                st.warning("Vui lòng nhập số tiền và nội dung!")
            else:
                now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
                # Tạo ID dạng chuỗi số giống hệt app Windows (thời gian mili-giây)
                tx_id = str(int(time.time() * 1000)) 
                
                # Cấu trúc dùng 'desc', 'date', 'amount' khớp 100% với Firebase
                new_item = {
                    "amount": float(gia_tri),
                    "date": now_str,
                    "desc": ly_do,
                    "type": loai_gd,
                    "user": st.session_state.current_user
                }
                
                fund_data[tx_id] = new_item

                # Lưu vào RAM
                if shop_id == "Shop Chính (Mặc định)":
                    st.session_state.db[DB_KEY] = fund_data
                else:
                    if "shops" not in st.session_state.db: st.session_state.db["shops"] = {}
                    if shop_id not in st.session_state.db["shops"]: st.session_state.db["shops"][shop_id] = {}
                    st.session_state.db["shops"][shop_id][DB_KEY] = fund_data

                # Bắn lên Firebase
                if save_fund_to_firebase(fund_data, shop_id):
                    st.success("✅ Đã ghi phiếu và đồng bộ thành công!")
                    time.sleep(1.5)
                    st.rerun()
