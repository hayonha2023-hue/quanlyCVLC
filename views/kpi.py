"""Write KPI records in the same emp/base/short/tgt/sold schema as HTCV."""
import streamlit as st
from views.workspace import page_header, sync_status
from services.app_data import number, kpi_records, kpi_table
from services.database import save, shop_path

s_float = number

def update_kpi_db(shop_id, employee, data):
    return save(shop_path(shop_id, 'kpi/emp/'+employee), data)

def render_kpi():
    shop=st.session_state.current_shop
    account=st.session_state.db.get('users',{}).get(st.session_state.user,{})
    if not (st.session_state.get('is_admin') or 'SỬA SỐ KPI' in (account.get('edit_permissions') or [])):
        st.warning('Tài khoản không có quyền sửa KPI.');return
    sync_status()
    page_header('Cập nhật KPI', 'Chọn nhân viên và điều chỉnh các số liệu cần cập nhật.', 'CHỈNH SỬA DỮ LIỆU')
    records,meta,schema=kpi_records(st.session_state.db,shop)
    values,_=kpi_table(st.session_state.db,shop)
    if values:st.dataframe(values,hide_index=True,use_container_width=True)
    if not records:
        st.info('Chưa có nhân viên KPI. Tạo bảng và chia target trên app trước.');return
    if schema != 'desktop':
        st.info('Đây là dữ liệu KPI của web cũ. Mở và lưu bảng KPI trong app để chuyển sang bảng dùng chung trước khi chỉnh sửa.');return
    person=st.selectbox('Nhân viên',list(records),key='kpi_person_'+shop)
    record=records[person]
    with st.form('kpi_edit_'+shop+'_'+person):
        base=st.number_input('Target gốc',value=int(number(record.get('base'))),step=1)
        short=st.number_input('Thiếu / dư tháng trước',value=int(number(record.get('short'))),step=1)
        sold=st.number_input('Đã bán',min_value=0,value=max(0,int(number(record.get('sold')))),step=1)
        if st.form_submit_button('Lưu KPI',type='primary'):
            update_kpi_db(shop,person,{'base':base,'short':short,'tgt':base+short,'sold':sold})
            st.success('Đã lưu KPI. App đọc lại Firebase sẽ nhận dữ liệu mới.')
