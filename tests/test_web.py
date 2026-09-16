import copy
from pathlib import Path
from unittest.mock import Mock
import pytest
import requests
from streamlit.testing.v1 import AppTest
from services import database
from services.auth import authenticate

DB={'users':{'admin':{'pass':'example-test-secret','role':'admin'},'staff':{'pass':'staff-test','role':'user'}},'shops':{'A':{},'B':{}}}

@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def blocked(*args,**kwargs):raise AssertionError('Live network prohibited in tests')
    monkeypatch.setattr(requests.sessions.Session,'request',blocked)

@pytest.fixture
def app(monkeypatch):
    monkeypatch.setattr(database,'request',lambda *a,**kw:copy.deepcopy(DB))
    at=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py'),default_timeout=15).run()
    return at

def login(at,user='admin',password='example-test-secret'):
    at.text_input[0].set_value(user)
    at.text_input[1].set_value(password)
    at.button[0].click().run()
    assert not at.exception
    return at

def test_login_no_default_bypass(app):
    login(app,password='123456')
    assert app.error
    assert not app.session_state.get('user') if hasattr(app.session_state,'get') else 'user' not in app.session_state

def test_existing_password():
    assert authenticate(DB,'admin','example-test-secret')
    assert authenticate(DB,'admin','admin') is None
    assert authenticate({},'admin','123456') is None

@pytest.mark.parametrize('menu',['🛒 Lịch Ecom','💰 Quỹ Shop','📋 Xem Lịch','📈 Theo Dõi KPI','📊 Chia Target','📍 Thị Trường','🤖 AI Tư Vấn','👥 Quản Trị Admin'])
def test_each_page_renders(app,menu):
    login(app)
    app.sidebar.radio[0].set_value(menu).run()
    assert not app.exception
    assert not [x.value for x in app.warning if 'bảo trì' in x.value]

def test_staff_cannot_see_admin(app):
    login(app,'staff','staff-test')
    assert '👥 Quản Trị Admin' not in app.sidebar.radio[0].options
    assert not app.sidebar.selectbox

@pytest.mark.parametrize('failure',[requests.Timeout(),requests.HTTPError('403'),ValueError('bad json')])
def test_request_failures(monkeypatch,failure):
    response=Mock()
    response.raise_for_status.side_effect=failure
    monkeypatch.setattr(requests,'request',Mock(return_value=response))
    with pytest.raises(database.DatabaseError):database.request('PATCH','users/test',{'pass':'test'})
    assert requests.request.call_args.kwargs['timeout']==(5,15)

def test_scalar_write_uses_put(monkeypatch):
    calls=[]
    monkeypatch.setattr(database,'request',lambda *a:calls.append(a))
    fake=Mock();fake.session_state=type('State',(dict,),{'__setattr__':dict.__setitem__})(db=copy.deepcopy(DB))
    monkeypatch.setattr(database,'st',fake)
    database.save('users/admin/bg_image','base64value')
    assert calls[0][0]=='PUT'
    assert fake.session_state['db']['users']['admin']['bg_image']=='base64value'

def test_failed_write_keeps_cache_and_stops(monkeypatch):
    class Stop(BaseException):pass
    monkeypatch.setattr(database,'request',Mock(side_effect=database.DatabaseError('offline')))
    fake=Mock();fake.session_state={'db':copy.deepcopy(DB)};fake.stop.side_effect=Stop
    monkeypatch.setattr(database,'st',fake)
    with pytest.raises(Stop):database.save('users/admin',{'pass':'changed'})
    assert fake.session_state['db']==DB
    fake.error.assert_called_once()

def test_patch_keeps_other_branches():
    source={'shops':{'A':{'one':1},'B':{'two':2}}}
    output=database.change_cache(source,'shops/A',{'one':3},'PATCH')
    assert output['shops']['B']=={'two':2}
    assert source['shops']['A']['one']==1

def test_kpi_numeric_does_not_multiply_decimal():
    from views.kpi import s_float
    assert s_float(12.5)==12.5

def test_failed_ecom_save_never_reports_success(app,monkeypatch):
    login(app)
    before=copy.deepcopy(app.session_state['db'])
    monkeypatch.setattr(database,'request',Mock(side_effect=database.DatabaseError('offline')))
    app.text_input[0].set_value('Changed')
    next(b for b in app.button if 'LƯU LỊCH ECOM' in b.label).click().run()
    assert app.error
    assert not app.success
    assert app.session_state['db']==before

def test_ecom_inputs_change_with_shop(app):
    login(app)
    app.text_input[0].set_value('Draft for main shop').run()
    app.sidebar.selectbox[0].set_value('A').run()
    assert app.text_input[0].value==''
    assert not app.exception

def test_staff_write_controls_disabled(app):
    login(app,'staff','staff-test')
    assert next(b for b in app.button if 'LƯU LỊCH ECOM' in b.label).disabled
    app.sidebar.radio[0].set_value('💰 Quỹ Shop').run()
    assert not [b for b in app.button if 'GHI PHIẾU' in b.label]
