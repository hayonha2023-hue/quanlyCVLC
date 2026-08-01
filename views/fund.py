import streamlit as st
import requests
import time

FIREBASE_URL = "https://htcv-5c857-default-rtdb.firebaseio.com/htcv.json"

def save_fund_to_firebase(fund_data, shop_id):
    try:
        url = FIREBASE_URL if shop_id == "Shop Chính (Mặc định)" else FIREBASE_URL.replace(".json", f"/shops/{shop_id}.json")
        requests.patch(url, json={"fund_history": fund_data}, timeout=10)
        return True
    except Exception as e:
        st.error(f"Lỗi đồng bộ: {e}")
        return False

def render_fund():
    st.markdown("""
    <div class='html-card'>
        <h3 class='html-title' style='text-align: left;'>💰 QUẢN LÝ QUỸ SHOP</h3>
        <p class='html-text' style='text-align: left; margin-bottom: 0px;'>Ghi chép các khoản Thu/Chi của chi nhánh</p>
    </div>
    """, unsafe_allow_html=True)

    shop_id = st.session_state.get("current_shop", "Shop Chính (Mặc định)")
    
    # Lấy dữ liệu quỹ từ bộ nhớ
    if shop_id == "Shop Chính (Mặc định)":
        fund_history = st.session_state.db.get("fund_history", [])
    else:
        fund_history = st.session_state.db.get("shops", {}).get(shop_id, {}).get("fund_history", [])
        
    if not isinstance(fund_history, list):
        fund_history = []

    # TÍNH TOÁN TỔNG QUỸ
    tong_thu = sum([int(item.get("amount", 0)) for item in fund_history if item.get("type") == "Thu"])
    tong_chi = sum([int(item.get("amount", 0)) for item in fund_history if item.get("type") == "Chi"])
    ton_quy = tong_thu - tong_chi

    col1, col2, col3 = st.columns(3)
    col1.metric("🟢 TỔNG THU", f"{tong_thu:,.0f} VNĐ")
    col2.metric("🔴 TỔNG CHI", f"{tong_chi:,.0f} VNĐ")
    col3.metric("💎 TỒN QUỸ", f"{ton_quy:,.0f} VNĐ")
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("**➕ THÊM GIAO DỊCH MỚI**")
    
    # Form nhập liệu
    with st.form("fund_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            gd_type = st.selectbox("Loại giao dịch", ["Thu", "Chi"])
            amount = st.number_input("Số tiền (VNĐ)", min_value=0, step=1000)
        with c2:
            reason = st.text_input("Lý do / Nội dung")
            date_str = st.date_input("Ngày giao dịch")
            
        submitted = st.form_submit_button("💾 LƯU GIAO DỊCH", type="primary", use_container_width=True)
        
        if submitted:
            if amount <= 0 or not reason:
                st.warning("Vui lòng nhập số tiền lớn hơn 0 và ghi rõ lý do!")
            else:
                new_tx = {
                    "date": date_str.strftime("%d/%m/%Y"),
                    "type": gd_type,
                    "amount": amount,
                    "reason": reason,
                    "user": st.session_state.current_user
                }
                fund_history.append(new_tx)
                
                # Cập nhật RAM Web
                if shop_id == "Shop Chính (Mặc định)":
                    st.session_state.db["fund_history"] = fund_history
                else:
                    if "shops" not in st.session_state.db: st.session_state.db["shops"] = {}
                    if shop_id not in st.session_state.db["shops"]: st.session_state.db["shops"][shop_id] = {}
                    st.session_state.db["shops"][shop_id]["fund_history"] = fund_history
                    
                # Bắn lên Mây Firebase
                if save_fund_to_firebase(fund_history, shop_id):
                    st.success("✅ Đã ghi nhận giao dịch thành công!")
                    time.sleep(1.5)
                    st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("**📜 LỊCH SỬ GIAO DỊCH**")
    if not fund_history:
        st.info("Chưa có giao dịch nào.")
    else:
        # Lật ngược danh sách để giao dịch mới nhất hiện lên đầu
        for item in reversed(fund_history): 
            color = "green" if item.get("type") == "Thu" else "red"
            sign = "+" if item.get("type") == "Thu" else "-"
            st.markdown(f"""
            <div style='padding: 10px; border: 1px solid #ddd; border-radius: 5px; margin-bottom: 10px; background-color: #f9f9f9;'>
                <span style='color: gray; font-size: 13px;'>📅 {item.get('date', '')} | 👤 {item.get('user', '').upper()}</span><br>
                <b>{item.get('reason', '')}</b>: <span style='color: {color}; font-weight: bold;'>{sign}{item.get('amount', 0):,.0f} đ</span>
            </div>
            """, unsafe_allow_html=True)
