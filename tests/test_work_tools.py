import copy
import io
import zipfile
from unittest.mock import Mock
import pandas as pd
import pytest
from PIL import Image
from streamlit.testing.v1 import AppTest
from services.workflows import make_draft, apply_schedule, schedule_token, split_workbook
from services.app_data import schedule_data
from services import database, schedule_store, kpi_scan

DB={'users':{'boss':{'pass':'fake','role':'super_admin'},'staff':{'pass':'fake','shop_id':'A','role':'user','edit_permissions':[]}},
    'settings':{'input_sáng':'An\nBình\nCúc\nDuy','input_chiều':'Em\nGiang\nHoa\nLan'},
    'shops':{'A':{'quy_shop':{'keep':'untouched'}},'B':{'private':'untouched'}},'phones':{'An':'0900000000'}}

@pytest.fixture(autouse=True)
def no_live(monkeypatch):
    monkeypatch.setattr('requests.sessions.Session.request',Mock(side_effect=AssertionError('No network in tests')))


def draft():
    return make_draft(DB['shops']['A'],{'Sáng':['An','Bình','Cúc','Duy'],'Chiều':['Em','Giang','Hoa','Lan']},['An'])


def test_schedule_compatible_and_scoped():
    d=draft(); result=apply_schedule(DB,'boss','A',d)
    hist,stats=schedule_data(result['shops']['A'])
    assert hist==d['history'] and stats==d['stats']
    assert len(hist)==7
    assert result['shops']['B']==DB['shops']['B']
    assert result['shops']['A']['quy_shop']==DB['shops']['A']['quy_shop']
    assert 'schedule_v2' not in DB['shops']['A']
    assert sum('An' in people for shifts in hist.values() for people in shifts.values())<=2
    for shifts in hist.values():
        people=[p for values in shifts.values() for p in values]
        assert len(people)==len(set(people))


def test_schedule_denies_other_shop_or_revoked_rights():
    db=copy.deepcopy(DB);db['users']['staff']['edit_permissions']=['CHIA LỊCH TỰ ĐỘNG']
    assert apply_schedule(db,'staff','A',draft())
    with pytest.raises(ValueError):apply_schedule(db,'staff','B',draft())
    with pytest.raises(ValueError):apply_schedule(DB,'staff','A',draft())


def test_schedule_lock_and_stale_draft():
    db=copy.deepcopy(DB);d=draft()
    db['shops']['A']['schedule_lock']={'locked':True}
    with pytest.raises(ValueError,match='chốt'):apply_schedule(db,'boss','A',d)
    db['shops']['A'].pop('schedule_lock');db['shops']['A']['stats']={'An':9}
    with pytest.raises(ValueError,match='thay đổi'):apply_schedule(db,'boss','A',d)


def test_repeat_save_does_not_double_stats():
    d=draft();updated=apply_schedule(DB,'boss','A',d)
    with pytest.raises(ValueError):apply_schedule(updated,'boss','A',d)


def test_conditional_save_conflict_and_failure(monkeypatch):
    response=Mock(headers={'ETag':'"revision"'});response.json.return_value=DB
    monkeypatch.setattr(schedule_store.requests,'get',Mock(return_value=response))
    put=Mock(return_value=Mock(status_code=412));monkeypatch.setattr(schedule_store.requests,'put',put)
    with pytest.raises(database.DatabaseError,match='thay đổi'):schedule_store.commit_schedule('boss','A',draft())
    assert put.call_args.kwargs['headers']=={'if-match':'"revision"'}


def workbook():
    b=io.BytesIO()
    with pd.ExcelWriter(b,engine='xlsxwriter',engine_kwargs={'options':{'strings_to_formulas':False}}) as writer:
        pd.DataFrame({'SĐT':['0012345678']*7,'Nội dung':['=1+1']+list('abcdef')}).to_excel(writer,index=False)
    return b.getvalue()


def test_split_keeps_rows_text_order_and_safe_names():
    raw,report=split_workbook(workbook(), 'data.xlsx', ['../An','Bình','Cúc'])
    assert [r['Số dòng'] for r in report]==[3,2,2]
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        frames=[pd.read_excel(io.BytesIO(z.read(p)),dtype=str) for p in z.namelist()]
        assert all('/' not in p and '\\' not in p for p in z.namelist())
        together=pd.concat(frames,ignore_index=True)
        assert len(together)==7 and set(together['SĐT'])=={'0012345678'}
        assert together.iloc[0]['Nội dung']=='=1+1'
        import openpyxl
        cell=openpyxl.load_workbook(io.BytesIO(z.read(z.namelist()[0]))).active['B2']
        assert cell.data_type=='s'


def test_split_more_people_than_rows():
    _,report=split_workbook(workbook(),'data.xlsx',[str(i) for i in range(9)])
    assert [r['Số dòng'] for r in report]==[1]*7+[0,0]


def test_split_missing_recipients():
    with pytest.raises(ValueError):split_workbook(workbook(),'data.xlsx',[])


def photo():
    out=io.BytesIO();Image.new('RGB',(30,20),'white').save(out,format='PNG');return out.getvalue()


def test_ai_real_payload_and_no_key_leak(monkeypatch):
    post=Mock(return_value=Mock(status_code=200))
    post.return_value.json.return_value={'choices':[{'message':{'content':'<think>private</think>Kết quả'}}]}
    monkeypatch.setattr(kpi_scan.requests,'post',post)
    assert kpi_scan.analyze(photo(),['secret-fake'])=='Kết quả'
    payload=post.call_args.kwargs['json']
    assert payload['messages'][0]['content'][1]['image_url']['url'].startswith('data:image/jpeg;base64,')
    assert post.call_args.kwargs['timeout']==(5,60)
    with pytest.raises(ValueError,match='Chưa có API'):kpi_scan.analyze(photo(),[])


def test_ai_failure_is_not_success(monkeypatch):
    monkeypatch.setattr(kpi_scan.requests,'post',Mock(return_value=Mock(status_code=429)))
    with pytest.raises(ValueError,match='chưa trả'):kpi_scan.analyze(photo(),['secret-fake'])
    with pytest.raises(ValueError):kpi_scan.image_bytes(b'not image')


def app_for(monkeypatch,user='boss'):
    monkeypatch.setattr(database,'request',lambda *a,**kw:copy.deepcopy(DB))
    a=AppTest.from_file(__import__('pathlib').Path(__file__).resolve().parents[1]/'app.py',default_timeout=20)
    a.session_state.user=user;a.session_state.db=copy.deepcopy(DB);a.session_state.current_shop='A'
    a.session_state.is_admin=user=='boss';a.session_state.is_super_admin=user=='boss'
    return a.run()


@pytest.mark.parametrize('page',['⚡ Sắp lịch & Đảo ca','🔍 Quét AI KPI','✂️ Chia Data'])
def test_new_pages_render(monkeypatch,page):
    a=app_for(monkeypatch);a.sidebar.button(key='nav_'+page).click().run()
    assert not a.exception
    from html import unescape
    heading = next(m.value for m in a.markdown if 'workspace-page-heading' in m.value and '<h1>' in m.value)
    expected = {'⚡ Sắp lịch & Đảo ca':'Sắp lịch & đảo ca', '🔍 Quét AI KPI':'Đọc ảnh KPI', '✂️ Chia Data':'Chia file Excel'}
    assert expected[page].casefold() in unescape(heading).casefold()


def test_swap_then_preview_no_automatic_write(monkeypatch):
    a=app_for(monkeypatch);a.sidebar.button(key='nav_'+'⚡ Sắp lịch & Đảo ca').click().run()
    old=a.text_area[0].value
    next(b for b in a.button if b.label=='Đảo danh sách Sáng ⇄ Chiều').click().run()
    assert a.text_area[1].value==old
    next(b for b in a.button if b.label=='Tạo lịch xem trước').click().run()
    assert not a.exception and len(a.dataframe)>0
    assert 'schedule_v2' not in a.session_state.db['shops']['A']


def test_staff_split_permission_message(monkeypatch):
    a=app_for(monkeypatch,'staff');a.sidebar.button(key='nav_'+'✂️ Chia Data').click().run()
    assert any('CHIA ĐỀU SỐ LIỆU' in m.value for m in a.info)
    assert not a.exception


def test_admin_tools_open_only_on_request(monkeypatch):
    a=app_for(monkeypatch)
    assert 'nav_👥 Quản Trị Admin' not in [b.key for b in a.sidebar.button]
    assert not [w for w in a.selectbox if w.key=='admin_task']
    a.button(key='open_admin_tools').click().run()
    assert not a.exception
    assert a.selectbox(key='admin_task').value=='Chọn tác vụ…'
    assert not a.multiselect
    a.selectbox(key='admin_task').set_value('Nhân sự & phân quyền').run()
    assert not a.multiselect
    a.selectbox(key='admin_employee_A').set_value('staff').run()
    assert len(a.multiselect)==2 and not a.exception
    a.button(key='open_admin_tools').click().run()
    assert 'nav_👥 Quản Trị Admin' not in [b.key for b in a.sidebar.button]
    assert not a.multiselect


def test_navigation_closes_editing(monkeypatch):
    a=app_for(monkeypatch)
    a.sidebar.button(key='nav_'+'🛒 Lịch Ecom').click().run()
    a.toggle[0].set_value(True).run()
    a.sidebar.button(key='nav_'+'💰 Quỹ Shop').click().run()
    a.sidebar.button(key='nav_'+'🛒 Lịch Ecom').click().run()
    assert not a.toggle[0].value
    assert not a.exception


def test_mobile_navigation_and_sidebar_stay_in_sync(monkeypatch):
    a=app_for(monkeypatch)
    a.selectbox(key='mobile_destination').set_value('🛒 Lịch Ecom').run()
    assert a.session_state.navigation == '🛒 Lịch Ecom'
    a.toggle[0].set_value(True).run()
    a.selectbox(key='mobile_destination').set_value('⚡ Sắp lịch & Đảo ca').run()
    assert not a.session_state['editing_🛒 Lịch Ecom']
    assert a.text_area and not a.exception
    a.sidebar.button(key='nav_🏠 Tổng quan').click().run()
    assert a.selectbox(key='mobile_destination').value == '🏠 Tổng quan'
    a.button(key='quick_🔍 Quét AI KPI').click().run()
    assert a.selectbox(key='mobile_destination').value == '🔍 Quét AI KPI'
    assert not a.exception


def test_mobile_staff_menu_excludes_administration(monkeypatch):
    a=app_for(monkeypatch,'staff')
    assert 'Quản trị' not in a.selectbox(key='mobile_destination').options
    assert not [b for b in a.button if b.key == 'open_admin_tools']
    a.selectbox(key='mobile_destination').set_value('✂️ Chia Data').run()
    assert any('CHIA ĐỀU SỐ LIỆU' in m.value for m in a.info)
    assert not a.exception
