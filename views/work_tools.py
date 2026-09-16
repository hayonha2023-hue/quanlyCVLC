"""Interactive workflows, scoped by account and shop; drafts survive reruns."""
import hashlib
import pandas as pd
import streamlit as st
from services.app_data import mapping, shop_data, schedule_data
from services.workflows import allowed, names, make_draft, split_workbook
from services.schedule_store import commit_schedule
from services.database import DatabaseError
from services.kpi_scan import analyze, image_bytes, PROMPT

TOOLS = ['⚡ Sắp lịch & Đảo ca','🔍 Quét AI KPI','✂️ Chia Data']


def _context():
    db=st.session_state.db
    return db, st.session_state.user, st.session_state.current_shop


def _identity(prefix):
    return prefix+'_'+st.session_state.user+'_'+st.session_state.current_shop


def _schedule_table(history):
    st.dataframe(pd.DataFrame([{'Ngày':day,**{shift:', '.join(staff) for shift,staff in shifts.items()}} for day,shifts in history.items()]),hide_index=True,use_container_width=True)


def render_schedule():
    db,user,shop=_context(); data=shop_data(db,shop); settings=mapping(db.get('settings'))
    st.title('Sắp lịch & Đảo ca')
    st.caption('Nhập nhân viên → Xem trước lịch tuần tới → Lưu để app và web cùng xem.')
    can_make=allowed(db,user,shop,'CHIA LỊCH TỰ ĐỘNG')
    can_swap=allowed(db,user,shop,'ĐẢO TÊN CA')
    prefix=_identity('schedule'); draft_key=prefix+'_draft'
    shifts=['Sáng','Chiều']+([] if 'CA 10H30' in (settings.get('hidden_features') or []) else ['10h30'])
    for shift in shifts:
        st.session_state.setdefault(prefix+shift,str(settings.get('input_'+shift.lower(),'') or ''))
    def swap():
        a,b=prefix+'Sáng',prefix+'Chiều'
        st.session_state[a],st.session_state[b]=st.session_state[b],st.session_state[a]
        st.session_state.pop(draft_key,None)
    st.subheader('1. Danh sách từng ca')
    st.button('Đảo danh sách Sáng ⇄ Chiều',on_click=swap,disabled=not can_swap,use_container_width=True)
    pools={}
    for column,shift in zip(st.columns(len(shifts)),shifts):
        with column:
            raw=st.text_area('Ca '+shift,key=prefix+shift,height=180,placeholder='Mỗi dòng một nhân viên')
            pools[shift]=names(raw)
            st.caption(f'{len(pools[shift])} nhân viên')
    special=st.text_input('Nhân viên đặc biệt (cách nhau bằng dấu phẩy)',value=str(settings.get('entry_ex','') or ''),key=prefix+'_special',help='Tối đa 2 ngày mỗi tuần, ưu tiên không liền nhau như app.')
    if not can_make: st.info('Quản trị cần cấp quyền CHIA LỊCH TỰ ĐỘNG để bạn tạo và lưu lịch.')
    locked=bool(mapping(data.get('schedule_lock')).get('locked'))
    if locked: st.warning('Lịch đang chốt. Quản trị cần mở khóa trong app trước khi sắp lại.')
    if st.button('Tạo lịch xem trước',type='primary',disabled=not can_make or locked,use_container_width=True):
        try:
            st.session_state[draft_key]=make_draft(data,pools,names(special))
        except ValueError as exc: st.error(str(exc))
    draft=st.session_state.get(draft_key)
    if draft:
        st.subheader('2. Kiểm tra lịch tuần tiếp theo')
        _schedule_table(draft['history'])
        short=sum(len(staff)<3 for shifts_ in draft['history'].values() for staff in shifts_.values())
        if short: st.warning(f'Có {short} ca dưới 3 người vì danh sách hoặc quy tắc không đủ người. Hãy kiểm tra trước khi lưu.')
        if st.button('Lưu lịch và đồng bộ',type='primary',disabled=not can_make or locked,use_container_width=True):
            try:
                st.session_state.db=commit_schedule(user,shop,draft)
            except (DatabaseError,ValueError) as exc: st.error(str(exc))
            else:
                st.session_state.pop(draft_key,None)
                st.success('Đã lưu lịch lên Firebase. App sẽ nhận lịch khi đồng bộ.')
    else:
        current,_=schedule_data(data)
        if current:
            with st.expander('Lịch hiện tại',expanded=True): _schedule_table(current)


def render_scanner():
    st.title('Quét AI KPI')
    st.caption('Tải ảnh bảng KPI để phân tích doanh số và kết quả từng nhân viên.')
    db,user,shop=_context(); prefix=_identity('scan')
    uploaded=st.file_uploader('1. Chọn ảnh KPI',type=['png','jpg','jpeg'],key=prefix+'_upload')
    keys=mapping(db.get('settings')).get('api_keys') or []
    if not isinstance(keys,list): keys=[]
    with st.expander('Kết nối AI'):
        st.caption('Đã có key cấu hình từ app.' if keys else 'Chưa có key cấu hình từ app.')
        session_key=st.text_input('API key Groq riêng (không bắt buộc)',type='password',key=prefix+'_key',help='Chỉ dùng trong phiên đăng nhập này, không lưu vào Firebase.')
    if session_key.strip(): keys=[session_key.strip()]
    if uploaded:
        raw=uploaded.getvalue(); stamp=hashlib.sha256(raw).hexdigest()
        try: preview=image_bytes(raw)
        except ValueError as exc: st.error(str(exc)); return
        with st.expander('Xem ảnh đã chọn',expanded=True): st.image(preview,width=600)
        st.caption('Khi bấm Phân tích, ảnh được gửi tới dịch vụ AI Groq. Kết quả không tự ghi vào số KPI.')
        if st.button('2. Phân tích ảnh KPI',type='primary',use_container_width=True):
            try:
                with st.spinner('Đang đọc bảng và phân tích KPI…'):
                    result=analyze(raw,keys)
                st.session_state[prefix+'_result']=(stamp,result)
            except ValueError as exc: st.error(str(exc))
        previous=st.session_state.get(prefix+'_result')
        if previous and previous[0]==stamp:
            st.subheader('Kết quả phân tích')
            st.markdown(previous[1])
            st.caption('Đối chiếu lại các con số với ảnh gốc trước khi sử dụng.')
            st.download_button('Tải kết quả',previous[1],file_name='Phan_tich_KPI.txt',mime='text/plain')
    with st.expander('Dùng Gemini trên web'):
        st.write('Sao chép câu lệnh dưới đây, mở Gemini rồi đính kèm ảnh KPI.')
        st.code(PROMPT,language=None)
        st.link_button('Mở Gemini','https://gemini.google.com/app')


def render_split():
    st.title('Chia Data')
    st.caption('Chia đều các dòng Excel theo thứ tự người nhận, tải tất cả trong một file ZIP.')
    db,user,shop=_context(); prefix=_identity('split')
    if not allowed(db,user,shop,'CHIA ĐỀU SỐ LIỆU'):
        st.info('Quản trị cần cấp quyền CHIA ĐỀU SỐ LIỆU để bạn sử dụng chức năng này.'); return
    uploaded=st.file_uploader('1. Chọn file Excel (tối đa 20 MB)',type=['xlsx','xls'],key=prefix+'_upload')
    contacts=list(mapping(db.get('phones')))
    history,_=schedule_data(shop_data(db,shop))
    st.subheader('2. Chọn người nhận')
    source=st.radio('Lấy danh sách từ',['Danh bạ','Lịch trực','Nhập tên'],horizontal=True,key=prefix+'_source')
    if source=='Lịch trực':
        if not history: st.info('Chi nhánh chưa có lịch trực.'); return
        day=st.selectbox('Ngày',list(history),key=prefix+'_day')
        shift=st.selectbox('Ca',list(history[day]),key=prefix+'_shift')
        options=names('\n'.join(history[day][shift]))
        recipients=st.multiselect('Người nhận',options,default=options,key=prefix+'_people_'+day+shift)
    elif source=='Danh bạ':
        recipients=st.multiselect('Người nhận',contacts,key=prefix+'_contacts')
    else:
        recipients=names(st.text_area('Mỗi dòng một người nhận',key=prefix+'_names'))
    st.caption(f'Đã chọn {len(recipients)} người. Các dòng dư được chia lần lượt từ người đầu tiên, như trên app.')
    if uploaded:
        content=uploaded.getvalue()
        signature=hashlib.sha256(content+'\n'.join(recipients).encode()).hexdigest()
        if st.button('3. Chia file',type='primary',disabled=not recipients,use_container_width=True):
            try:
                with st.spinner('Đang chia file…'): archive,report=split_workbook(content,uploaded.name,recipients)
                st.session_state[prefix+'_result']=(signature,archive,report)
            except Exception as exc:
                st.error(str(exc) if isinstance(exc,ValueError) else 'Không đọc được file Excel. Kiểm tra file không bị khóa hoặc hỏng rồi thử lại.')
        result=st.session_state.get(prefix+'_result')
        if result and result[0]==signature:
            st.success('Đã chia xong. Bấm tải ZIP bên dưới để lấy các file.')
            st.dataframe(result[2],hide_index=True,use_container_width=True)
            st.download_button('Tải tất cả file ZIP',result[1],file_name='HTCV_Data_da_chia.zip',mime='application/zip',type='primary',use_container_width=True)
            if st.button('Dọn kết quả khỏi phiên web'):
                st.session_state.pop(prefix+'_result',None); st.rerun()
    st.caption('Web chia và tải file; gửi tự động qua Zalo PC vẫn dùng trên app máy tính.')


def render_tool(page):
    {TOOLS[0]:render_schedule,TOOLS[1]:render_scanner,TOOLS[2]:render_split}[page]()
