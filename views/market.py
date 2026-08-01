import streamlit as st
import pandas as pd

def render_market():
    st.markdown("<h3 style='margin-top: 0px; margin-bottom: 25px; font-weight:800;'>📍 Bản Đồ Phân Công Công Tác Thị Trường</h3>", unsafe_allow_html=True)
    
    shop_id = st.session_state.get("current_shop", "Shop Chính (Mặc định)")
    full_db = st.session_state.get("db", {})
    db = full_db if shop_id == "Shop Chính (Mặc định)" else full_db.get("shops", {}).get(shop_id, {})
    
    market_data = db.get("market_history", {})
    if not market_data:
        st.info("📌 Chưa có lịch phân công tác thị trường.")
    else:
        market_list = [{"Kế hoạch Ngày": d, "📍 Địa Điểm": inf.get("dia_diem", ""), "👥 Tuyến": ", ".join(inf.get("nhan_vien", []))} for d, inf in market_data.items()]
        st.dataframe(pd.DataFrame(market_list), hide_index=True, use_container_width=True)
