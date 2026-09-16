"""Employee read views for all business data the desktop publishes to Firebase."""
import base64
import io
import pandas as pd
import streamlit as st
from PIL import Image
from services.app_data import mapping, rows, snapshot, kpi_table, target_tables, number

PAGES = {
    '🏠 Tổng quan':'overview', '📋 Xem Lịch':'schedule', '📊 Tích Lũy':'stats',
    '📈 Theo Dõi KPI':'kpi', '📊 Target Ngày':'target', '🛒 Lịch Ecom':'ecom',
    '💰 Quỹ Shop':'fund', '📍 Thị Trường':'market', '📞 Danh Bạ':'phones',
}

def table(items, label, key):
    if not items:
        st.info('Chưa có dữ liệu ' + label.lower() + ' được lưu từ app.')
        return
    df=pd.DataFrame(items).fillna('')
    st.dataframe(df, hide_index=True, use_container_width=True)
    st.download_button('Tải bảng ' + label, df.to_csv(index=False).encode('utf-8-sig'),
                       file_name=key+'.csv', mime='text/csv', key='download_'+key)

def gallery(value, label):
    if isinstance(value, str): value=[value]
    images=rows(value)
    if not images:
        st.info('Chưa có ' + label.lower() + ' từ app.')
    for i,item in enumerate(images):
        name=f'{label} {i+1}'
        if isinstance(item,dict):
            name=str(item.get('name') or name)
            item=item.get('data',item.get('base64',item.get('image','')))
        if not isinstance(item,str):continue
        try:
            encoded=item.split(',',1)[1] if item.startswith('data:') else item
            binary=base64.b64decode(encoded,validate=True)
            with Image.open(io.BytesIO(binary)) as picture: picture.verify()
            st.image(binary,caption=name,use_container_width=True)
        except (ValueError,OSError,Image.DecompressionBombError):
            st.warning(name + ': dữ liệu ảnh không đọc được. Hãy tải lại ảnh từ app.')

def schedule(d):
    tabs=st.tabs(['Lịch theo ca','Ảnh lịch','Lịch sử sửa'])
    with tabs[0]:
        state=mapping(d.get('schedule_lock'))
        if state.get('locked'): st.info('Lịch đã chốt trên app.')
        result=[]
        for day,shifts in mapping(d.get('detailed_history')).items():
            for shift,names in mapping(shifts).items():
                result.append({'Ngày':day,'Ca':shift,'Nhân viên':', '.join(map(str,names)) if isinstance(names,list) else str(names)})
        table(result,'Lịch trực','lich_truc')
    with tabs[1]: gallery(d.get('schedule_images'),'Ảnh lịch')
    with tabs[2]:
        # Only scheduling log entries, never user records or credentials.
        logs=rows(d.get('schedule_edit_log'))
        if logs:
            for i,log in enumerate(logs[:100]):
                if isinstance(log,dict):
                    with st.expander('Lần sửa '+str(i+1)): st.json(log)
        else: st.info('Chưa có lịch sử sửa lịch.')

def stats(d):
    result=[]
    for name,value in mapping(d.get('stats')).items():
        if not isinstance(value,dict):continue
        result.append({'Nhân viên':name,'Tổng ca':value.get('ca',0),'Sáng':value.get('Sáng',0),
                       'Chiều':value.get('Chiều',0),'10h30':value.get('10h30',0)})
    table(result,'Tích lũy','tich_luy')

def kpi(db,d):
    tabs=st.tabs(['KPI tháng','Ảnh KPI'])
    with tabs[0]:
        result,meta=kpi_table(db,d['shop'])
        if meta: st.caption(f"Tháng: {meta.get('m','')} • Tổng target: {meta.get('tot',0)}")
        table(result,'KPI','kpi')
    with tabs[1]: gallery(d.get('kpi_images'),'Ảnh KPI')

def target(d):
    data=mapping(d.get('daily_targets')); result=mapping(data.get('results'))
    if data.get('date_updated'):
        st.caption('App chốt lúc '+str(data['date_updated'])+' • '+str(data.get('updated_by','')))
    columns=st.columns(3)
    columns[0].metric('Nhân sự',result.get('nv',data.get('nv','—')))
    columns[1].metric('Nhân sự ca sáng',result.get('staff_ca1',data.get('staff_ca1','—')))
    columns[2].metric('Nhân sự ca chiều',result.get('staff_ca2',data.get('staff_ca2','—')))
    inputs,outputs=target_tables(data)
    tabs=st.tabs(['Kết quả / người','Kết quả / ca','Ca / người','Số liệu đầu vào'])
    for tab,key,label in zip(tabs,outputs,('Target mỗi người','Target mỗi ca','Target ca mỗi người')):
        with tab: table(outputs[key],label,key)
    with tabs[3]: table(inputs,'Đầu vào Target','target_inputs')
    if data and not result:
        st.info('App chưa lưu kết quả đã tính. Mở Target Ngày trên app và bấm Lưu để xem đúng kết quả đã chốt ở đây.')

def ecom(d):
    data=mapping(d.get('ecom_history')); order=['Thứ 2','Thứ 3','Thứ 4','Thứ 5','Thứ 6','Thứ 7','Chủ Nhật']
    table([{'Ngày':day,'Sáng':mapping(data[day]).get('Sáng',data[day] if isinstance(data[day],str) else ''),
            'Chiều':mapping(data[day]).get('Chiều','')} for day in order+sorted(set(data)-set(order)) if day in data], 'Lịch Ecom','ecom')

def fund(d):
    items=[v for v in mapping(d.get('quy_shop')).values() if isinstance(v,dict)]
    total=lambda kind:sum(number(v.get('amount')) for v in items if v.get('type')==kind)
    cols=st.columns(4)
    for col,label,value in zip(cols,['Tồn quỹ','Tổng thu','Tổng chi','Chi riêng'],[total('Thu')-total('Chi')-total('Chi Riêng'),total('Thu'),total('Chi'),total('Chi Riêng')]):
        col.metric(label,f'{value:,.0f} đ')
    table([{'Ngày':v.get('date',''),'Loại':v.get('type',''),'Số tiền':number(v.get('amount')),
            'Nội dung':v.get('desc',''),'Người ghi':v.get('user','')} for v in reversed(items)],'Quỹ shop','quy_shop')

def market(d):
    table([{'Ngày':date,'Địa điểm':v.get('dia_diem',''),'Nhân viên':', '.join(map(str,rows(v.get('nhan_vien'))))}
           for date,v in mapping(d.get('market_history')).items() if isinstance(v,dict)],'Thị trường','thi_truong')

def phones(d):
    query=st.text_input('Tìm tên hoặc số điện thoại',key='find_phone').casefold().strip()
    table([{'Tên':name,'Số điện thoại':str(phone)} for name,phone in mapping(d.get('phones')).items()
           if not isinstance(phone,(dict,list)) and query in (str(name)+' '+str(phone)).casefold()], 'Danh bạ nội bộ','danh_ba')

def overview(db,d):
    st.markdown('<div class="htcv-hero"><h2>Công việc trong tầm tay</h2><p>Sắp lịch, đọc KPI và chia dữ liệu từ một nơi.</p></div>', unsafe_allow_html=True)
    result,meta=kpi_table(db,d['shop'])
    cols=st.columns(3)
    cols[0].metric('Ngày có lịch',len(mapping(d.get('detailed_history'))))
    cols[1].metric('Nhân sự KPI',len(result))
    cols[2].metric('Liên hệ',len(mapping(d.get('phones'))))
    st.subheader('Công cụ làm việc')
    from views.work_tools import TOOLS
    def go(page):
        st.session_state.navigation=page
        st.session_state.show_bg=False
        st.session_state.show_pass=False
    for col,page,description in zip(st.columns(3),TOOLS,[
        'Đảo danh sách ca, tạo lịch tuần tới và đồng bộ với app.',
        'Tải ảnh KPI, đọc phân tích và tải kết quả.',
        'Chọn người nhận, chia Excel và tải trọn bộ ZIP.'
    ]):
        with col.container(border=True):
            st.markdown('### '+page)
            st.write(description)
            st.button('Mở chức năng',key='quick_'+page,on_click=go,args=(page,),use_container_width=True)
    st.subheader('Dữ liệu nhân viên có thể xem')
    st.write('Lịch trực và ảnh lịch · Tích lũy ca · KPI và ảnh KPI · Target Ngày đã chốt · Ecom · Quỹ Shop · Thị Trường · Danh Bạ')
    st.caption('Chọn chức năng ở menu bên trái. Trên điện thoại, mở menu bằng nút ở góc trên bên trái.')
    with st.expander('Các file làm việc trên máy tính'):
        st.write('Chia Data đã có trong mục Công cụ làm việc. File Lập Hàng và thao tác gửi Zalo PC vẫn dùng trên app máy tính.')
    st.subheader('Lịch trực đã lưu')
    schedule(d)

def render_employee(page):
    db=st.session_state.get('db',{});d=snapshot(db,st.session_state.current_shop)
    st.subheader(page)
    if PAGES[page]=='overview':overview(db,d)
    elif PAGES[page]=='kpi':kpi(db,d)
    else:globals()[PAGES[page]](d)
