"""Employee read views for all business data the desktop publishes to Firebase."""
import base64
import io
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
from PIL import Image
from services.app_data import mapping, rows, snapshot, kpi_table, target_tables, number
from views.workspace import navigate, page_header, empty_state, ICONS

PAGES = {
    '🏠 Tổng quan':'overview', '📋 Xem Lịch':'schedule', '📊 Tích Lũy':'stats',
    '📈 Theo Dõi KPI':'kpi', '📊 Target Ngày':'target', '🛒 Lịch Ecom':'ecom',
    '💰 Quỹ Shop':'fund', '📍 Thị Trường':'market', '📞 Danh Bạ':'phones',
}

def table(items, label, key):
    if not items:
        empty_state('Chưa có dữ liệu', 'Dữ liệu '+label.lower()+' sẽ xuất hiện khi được lưu và đồng bộ.')
        return
    df=pd.DataFrame(items).fillna('')
    if len(df)>8:
        query=st.text_input('Tìm trong bảng',key='search_'+key,placeholder='Nhập tên hoặc nội dung cần tìm').strip().casefold()
        if query:
            df=df[df.astype(str).apply(lambda col:col.str.casefold().str.contains(query,regex=False)).any(axis=1)]
    st.caption(f'{len(df):,} dòng · {label}')
    if df.empty:
        empty_state('Không tìm thấy kết quả', 'Thử tên hoặc từ khóa khác.')
    else:
        st.dataframe(df, hide_index=True, use_container_width=True)
    st.download_button('Tải CSV', df.to_csv(index=False).encode('utf-8-sig'),
                       file_name=key+'.csv', mime='text/csv', key='download_'+key, icon=':material/download:')

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
    from views.schedule_board import render_board, people, name_key
    tabs=st.tabs(['Lịch theo ngày','Bảng & tải lịch','Ảnh lịch','Lịch sử sửa'])
    history=mapping(d.get('detailed_history'))
    selected_history=history
    query=''
    with tabs[0]:
        if mapping(d.get('schedule_lock')).get('locked'): st.info('Lịch đã chốt trên app.')
        if history:
            left,right=st.columns(2)
            selected=left.selectbox('Ngày làm việc',['Tất cả ngày']+list(history),key='schedule_day_'+d['shop'])
            query=right.text_input('Tìm nhân viên',placeholder='Nhập tên để tìm ca làm',key='schedule_person_'+d['shop']).strip()
            if selected!='Tất cả ngày': selected_history={selected:history[selected]}
            st.caption('Tìm tên có dấu hoặc không dấu. Tên phù hợp được viền đậm trong ca làm.')
            render_board(selected_history,query)
        else:
            empty_state('Chưa có lịch làm việc', 'Lịch sẽ xuất hiện sau khi được lưu và đồng bộ.')
    with tabs[1]:
        result=[]
        for day,shifts in selected_history.items():
            if query and not any(name_key(query) in name_key(name) for value in mapping(shifts).values() for name in people(value)): continue
            for shift,staff in mapping(shifts).items():
                result.append({'Ngày':day,'Ca':shift,'Nhân viên':', '.join(people(staff))})
        table(result,'Lịch trực','lich_truc')
    with tabs[2]: gallery(d.get('schedule_images'),'Ảnh lịch')
    with tabs[3]:
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
        from views.target_cards import render_cards, display_number
        if meta: st.caption(f"Tháng {meta.get('m','')} · Tổng target đã lưu: {display_number(meta.get('tot'))}")
        if result:
            person=st.selectbox('Xem nhanh KPI của nhân viên',[row['Nhân viên'] for row in result],key='kpi_summary_'+d['shop'])
            row=next(row for row in result if row['Nhân viên']==person)
            render_cards([dict(row,**{'Chỉ số':person})],[
                ('Target tháng','CHỈ TIÊU THÁNG','goal'),('Đã bán','ĐÃ BÁN','done'),
                ('Còn thiếu','CÒN THIẾU','remaining'),('Vượt','VƯỢT CHỈ TIÊU','done')])
            if row['Target tháng']>0:
                st.progress(min(1.0,max(0.0,row['Hoàn thành (%)']/100)),text='Hoàn thành '+display_number(row['Hoàn thành (%)'])+'%')
            else: st.caption('Chưa có chỉ tiêu dương để tính tỷ lệ hoàn thành.')
        with st.expander('Bảng KPI đầy đủ và tải file'):
            table(result,'KPI','kpi')
    with tabs[1]: gallery(d.get('kpi_images'),'Ảnh KPI')

def target(d):
    data=mapping(d.get('daily_targets')); result=mapping(data.get('results'))
    if data.get('date_updated'):
        st.caption('App chốt lúc '+str(data['date_updated'])+' • '+str(data.get('updated_by','')))
    from views.target_cards import render_cards, display_number
    with st.expander('Nhân sự dùng để chia target'):
        columns=st.columns(3)
        columns[0].metric('Tổng nhân sự',display_number(result.get('nv',data.get('nv'))))
        columns[1].metric('Ca sáng',display_number(result.get('staff_ca1',data.get('staff_ca1'))))
        columns[2].metric('Ca chiều',display_number(result.get('staff_ca2',data.get('staff_ca2'))))
    inputs,outputs=target_tables(data)
    units={name:str(record.get('unit') or record.get('don_vi') or '') for name,record in mapping(data.get('metrics')).items() if isinstance(record,dict)}
    tabs=st.tabs(['Mỗi người','Tổng từng ca','Mỗi người trong ca','Số liệu gốc'])
    scopes=[
        ('per_employee','Target mỗi người',[('Ngày / người','MỖI NGƯỜI / NGÀY','goal'),('Tháng / người','MỖI NGƯỜI / THÁNG','neutral')]),
        ('per_shift','Target mỗi ca',[('Tổng ngày','TỔNG CẢ NGÀY','goal'),('Ca sáng','CA SÁNG','neutral'),('Ca chiều','CA CHIỀU','neutral')]),
        ('per_shift_person','Target ca mỗi người',[('Ca sáng / người','MỖI NGƯỜI / CA SÁNG','goal'),('Ca chiều / người','MỖI NGƯỜI / CA CHIỀU','neutral')]),
    ]
    for tab,(key,label,fields) in zip(tabs,scopes):
        with tab:
            render_cards(outputs[key],fields,units)
            if outputs[key]:
                with st.expander('Xem bảng và tải file'):
                    table(outputs[key],label,key)
            else: empty_state('Chưa có kết quả đã lưu', 'Lưu kết quả Target ngày trên app để xem tại đây.')
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
    now = datetime.now(ZoneInfo('Asia/Ho_Chi_Minh'))
    day_name = ['Thứ Hai','Thứ Ba','Thứ Tư','Thứ Năm','Thứ Sáu','Thứ Bảy','Chủ nhật'][now.weekday()]
    page_header('Tổng quan', f'{day_name}, {now:%d/%m/%Y}')
    result,meta=kpi_table(db,d['shop'])
    from views.work_tools import TOOLS
    with st.container(key='overview_tools'):
        for col,page,label in zip(st.columns(3), TOOLS, ['Sắp lịch & đảo ca', 'Quét AI KPI', 'Chia data']):
            col.button(label, icon=ICONS[page], key='quick_'+page, on_click=navigate, args=(page,), use_container_width=True)
    st.markdown('<div class="workspace-section-title">Dữ liệu chi nhánh</div>', unsafe_allow_html=True)
    with st.container(key='overview_metrics'):
        cols=st.columns(3)
        cols[0].metric('Ngày có lịch',len(mapping(d.get('detailed_history'))), help='Số ngày trong lịch đang lưu của chi nhánh.')
        cols[1].metric('Nhân sự KPI',len(result), help='Số nhân viên có dữ liệu trong bảng KPI của chi nhánh.')
        cols[2].metric('Liên hệ',len(mapping(d.get('phones'))), help='Số liên hệ trong danh bạ chung.')
    st.markdown('<div class="workspace-section-title">Lịch làm việc</div>', unsafe_allow_html=True)
    with st.container(border=True):
        schedule(d)
    with st.expander('Các file làm việc trên máy tính'):
        st.write('Chia Data đã có trong mục Công cụ làm việc. File Lập Hàng và thao tác gửi Zalo PC vẫn dùng trên app máy tính.')

def render_employee(page):
    db=st.session_state.get('db',{});d=snapshot(db,st.session_state.current_shop)
    if PAGES[page]=='overview':
        overview(db,d)
        return
    descriptions = {
        'schedule': ('Lịch làm việc', 'Theo dõi các ca làm, ảnh lịch và lịch sử điều chỉnh.'),
        'stats': ('Tích lũy ca làm', 'Tổng số ca và phân bổ ca làm của từng nhân viên.'),
        'kpi': ('KPI tháng', 'Đối chiếu chỉ tiêu, kết quả đã bán và mức hoàn thành của đội ngũ.'),
        'target': ('Target ngày', 'Xem chỉ tiêu mỗi người, mỗi ca và số liệu đã chốt.'),
        'ecom': ('Lịch Ecom', 'Phân công ca sáng và ca chiều theo từng ngày trong tuần.'),
        'fund': ('Quỹ shop', 'Theo dõi số dư, thu chi và chi tiết các phiếu quỹ.'),
        'market': ('Lịch thị trường', 'Tra cứu tuyến, địa điểm và nhân viên được phân công.'),
        'phones': ('Danh bạ', 'Tìm nhanh tên và số điện thoại trong danh bạ nội bộ.'),
    }
    title,description=descriptions[PAGES[page]]
    page_header(title,description,'DỮ LIỆU & BÁO CÁO')
    with st.container(border=True, key='workspace_report'):
        if PAGES[page]=='kpi':kpi(db,d)
        else:globals()[PAGES[page]](d)
