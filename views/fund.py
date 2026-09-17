from views.workspace import page_header, sync_status
import copy
import pandas as pd
from services.database import save, shop_path
import streamlit as st
import requests
import time
from datetime import datetime

FIREBASE_URL = "https://htcv-5c857-default-rtdb.firebaseio.com/htcv.json"
DB_KEY = "quy_shop"

def save_fund_to_firebase(fund_data, shop_id):
    return save(shop_path(shop_id), {DB_KEY: fund_data})

def render_fund():
    sync_status()
    page_header('Quản lý quỹ shop', 'Theo dõi thu chi và ghi phiếu cho chi nhánh đang chọn.', 'CHỈNH SỬA DỮ LIỆU')

    shop_id = st.session_state.get("current_shop", "Shop Chính (Mặc định)")

    # 1. Kéo dữ liệu dạng Từ điển (Dict) chuẩn theo Firebase của bạn
    if shop_id == "Shop Chính (Mặc định)":
        fund_data = st.session_state.db.get(DB_KEY, {})
    else:
        fund_data = st.session_state.db.get("shops", {}).get(shop_id, {}).get(DB_KEY, {})

    if not isinstance(fund_data, dict):
        fund_data = {}

    fund_data = copy.deepcopy(fund_data)

    # 2. Tính toán 4 chỉ số (Khớp hoàn toàn form Windows)
    tong_thu = sum([float(item.get("amount", 0)) for item in fund_data.values() if item.get("type") == "Thu"])
    tong_chi = sum([float(item.get("amount", 0)) for item in fund_data.values() if item.get("type") == "Chi"])
    chi_rieng = sum([float(item.get("amount", 0)) for item in fund_data.values() if item.get("type") == "Chi Riêng"])
    ton_quy = tong_thu - tong_chi - chi_rieng

    # 3. Hiển thị 4 Khối Thống Kê
    for col, label, value in zip(st.columns(4), ['Tồn quỹ','Tổng thu','Tổng chi','Chi riêng'], [ton_quy,tong_thu,tong_chi,chi_rieng]):
        col.metric(label, f'{value:,.0f} ₫')

    # 4. Hiển thị Danh sách Giao Dịch
    # Sắp xếp theo ID (chuỗi số thời gian) để cái mới nhất nổi lên đầu
    sorted_funds = sorted(fund_data.items(), key=lambda x: x[0], reverse=True)

    if sorted_funds:
        st.dataframe(pd.DataFrame([{
            'Ngày': item.get('date',''), 'Loại': item.get('type',''),
            'Số tiền': float(item.get('amount',0)), 'Nội dung': item.get('desc',''),
            'Người ghi': item.get('user',''),
        } for _,item in sorted_funds]), hide_index=True, use_container_width=True)
    else:
        st.info('Chưa có phiếu thu chi. Bạn có thể ghi phiếu đầu tiên bên dưới.')

    account = st.session_state.db.get('users', {}).get(st.session_state.get('user', ''), {})
    if not (st.session_state.get('is_admin', False) or 'QUẢN LÝ QUỸ SHOP' in account.get('edit_permissions', [])):
        st.caption('Bạn có quyền xem quỹ. Liên hệ quản trị để được cấp quyền ghi phiếu.')
        return

    # 5. Form nhập liệu Ghi Phiếu (Dàn hàng ngang dưới cùng)
    with st.form("fund_form", clear_on_submit=False):
        st.subheader("Ghi phiếu thu chi")
        col1, col2, col3 = st.columns([2, 3, 5])
        with col1:
            loai_gd = st.selectbox("Loại phiếu", ["Thu", "Chi", "Chi Riêng"], label_visibility="visible")
        with col2:
            gia_tri = st.number_input("Số tiền (đồng)", min_value=0, step=1000, label_visibility="visible", placeholder="Nhập số tiền...")
        with col3:
            ly_do = st.text_input("Lý do", label_visibility="visible", placeholder="Nội dung...")
        submit = st.form_submit_button("Lưu phiếu", type="primary", use_container_width=True)

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

                # Bắn lên Firebase
                if save_fund_to_firebase(fund_data, shop_id):
                    st.success("✅ Đã ghi phiếu và đồng bộ thành công!")
                    time.sleep(1.5)
                    st.rerun()
