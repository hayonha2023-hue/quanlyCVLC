"""Fixtures use the exact desktop schema, never real accounts or live Firebase."""
import ast
import copy
from pathlib import Path
from unittest.mock import Mock
import pytest
from streamlit.testing.v1 import AppTest
from services import database, sync
from services.app_data import DEFAULT_SHOP, snapshot, kpi_table, target_tables
from services.auth import authenticate

A={
 'schedule_v2':{'schema_version':2,'deleted':False,'days':[{'date_label':'16/09 - Thứ Tư','shifts':[{'name':'Sáng','staff':['An']},{'name':'10h30','staff':['Bình']}]}],
                'stats':[{'name':'An','value':{'ca':12,'Sáng':5,'Chiều':6,'10h30':1}}]},
 'detailed_history':{'OLD':{'Sáng':['MUST_NOT_APPEAR']}},
 'kpi':{'m':9,'tot':120,'emp':{'An':{'base':100,'short':20,'tgt':120,'sold':90}}},
 'daily_targets':{'nv':'2','ca1':'60','ca2':'40','staff_ca1':'1','staff_ca2':'1','updated_by':'manager','date_updated':'08:00 ngày 16/09/2026',
   'metrics':{'Doanh số':{'goc':'1000','pct':'100','thang':'800','ngay':'40'}},
   'results':{'schema':1,'nv':2,'staff_ca1':1,'staff_ca2':1,'per_employee':{'Doanh số':{'thang':400,'ngay':20}},
              'per_shift':{'Doanh số':{'tong_ngay':40,'ca1':24,'ca2':16}},'per_shift_person':{'Doanh số':{'ca1':24,'ca2':16}}}},
 'ecom_history':{'Thứ 2':{'Sáng':'An','Chiều':'Bình'}},
 'quy_shop':{'1':{'date':'16/09/2026','type':'Thu','amount':200,'desc':'Quỹ tháng','user':'manager'}},
 'market_history':{'16-09-2026':{'dia_diem':'Tuyến A','nhan_vien':['An']}}
}
CLOUD={'users':{'staff':{'pass':'test-password','role':'user','shop_id':'A'},'admin':{'pass':'test-admin','role':'super_admin'}},
       'shops':{'A':A,'B':{'kpi':{'emp':{'PRIVATE_B':{'base':999,'tgt':999,'sold':0}}}}},
       'phones':{'An':'0912000000'},'settings':{'api_keys':['NOT_FOR_EMPLOYEES']},
       'kpi':{'A':{'OUTDATED_LEGACY':{'target':999,'achieved':0,'debt':0}}}}

@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    import requests
    monkeypatch.setattr(requests.sessions.Session,'request',Mock(side_effect=AssertionError('No live network allowed')))

@pytest.fixture
def staff(monkeypatch):
    monkeypatch.setattr(database,'request',lambda *a,**kw:copy.deepcopy(CLOUD))
    app=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py'),default_timeout=15).run()
    app.text_input[0].set_value('staff');app.text_input[1].set_value('test-password')
    app.button[0].click().run()
    assert not app.exception
    return app

def test_scope_and_no_credentials():
    d=snapshot(CLOUD,'A')
    assert d['detailed_history']['16/09 - Thứ Tư']['Sáng']==['An']
    assert d['stats']['An']['ca']==12
    assert 'users' not in d and 'settings' not in d
    assert 'PRIVATE_B' not in str(d)
    assert 'NOT_FOR_EMPLOYEES' not in str(d)

def test_deleted_v2_never_resurrects_legacy():
    cloud=copy.deepcopy(CLOUD);cloud['shops']['A']['schedule_v2']={'schema_version':2,'deleted':True}
    d=snapshot(cloud,'A')
    assert d['detailed_history']=={} and d['stats']=={}

def test_empty_v2_beats_old_history():
    cloud=copy.deepcopy(CLOUD);cloud['shops']['A']['schedule_v2']={'schema_version':2,'days':[],'stats':[]}
    assert snapshot(cloud,'A')['detailed_history']=={}

def test_legacy_date_slash_compatibility():
    d=snapshot({'detailed_history':{'16':{'09 - Thứ Tư':{'Sáng':['An']}}}},DEFAULT_SHOP)
    assert d['detailed_history']=={'16/09 - Thứ Tư':{'Sáng':['An']}}

def test_kpi_uses_desktop_not_old_web_branch():
    result,meta=kpi_table(CLOUD,'A')
    assert len(result)==1 and result[0]['Nhân viên']=='An'
    assert result[0]['Target tháng']==120 and result[0]['Đã bán']==90
    assert result[0]['Còn thiếu']==30 and result[0]['Hoàn thành (%)']==75
    assert meta['m']==9

def test_canonical_empty_kpi_does_not_resurrect_legacy():
    cloud=copy.deepcopy(CLOUD);cloud['shops']['A']['kpi']={'m':9,'tot':0}
    assert kpi_table(cloud,'A')[0]==[]

def test_target_shows_saved_snapshot_without_recalculation():
    target=copy.deepcopy(A['daily_targets']);target['metrics']['Doanh số']['ngay']='99999'
    inputs,out=target_tables(target)
    assert inputs[0]['Ngày cần bán']=='99999'
    assert out['per_shift'][0]['Ca sáng']==24
    assert out['per_employee'][0]['Ngày / người']==20

@pytest.mark.parametrize('menu',['🏠 Tổng quan','📋 Xem Lịch','📊 Tích Lũy','📈 Theo Dõi KPI','📊 Target Ngày','🛒 Lịch Ecom','💰 Quỹ Shop','📍 Thị Trường','📞 Danh Bạ'])
def test_staff_sees_populated_app_data(staff,menu,monkeypatch):
    writes=[]
    def request(method,*args,**kwargs):
        if method!='GET': writes.append(method)
        return copy.deepcopy(CLOUD)
    monkeypatch.setattr(database,'request',request)
    staff.sidebar.button(key='nav_'+menu).click().run()
    assert not staff.exception
    assert staff.dataframe
    assert not writes
    assert not staff.sidebar.toggle
    displayed=' '.join(str(frame.value) for frame in staff.dataframe)
    assert 'PRIVATE_B' not in displayed and 'OUTDATED_LEGACY' not in displayed
    assert 'NOT_FOR_EMPLOYEES' not in displayed and 'test-password' not in displayed

def test_refresh_picks_up_app_change(staff,monkeypatch):
    updated=copy.deepcopy(CLOUD);updated['shops']['A']['kpi']['emp']['An']['sold']=119
    monkeypatch.setattr(database,'request',lambda *a,**kw:updated)
    staff.sidebar.button(key='nav_'+'📈 Theo Dõi KPI').click().run()
    assert staff.dataframe[0].value.iloc[0]['Đã bán']==119

def test_server_delete_replaces_old_session_data(monkeypatch):
    state={'user':'staff','db':copy.deepcopy(CLOUD),'current_shop':'A'}
    deleted=copy.deepcopy(CLOUD);deleted['shops']['A']={}
    monkeypatch.setattr(sync,'fetch_data',lambda:deleted)
    assert sync.refresh(state,True)
    assert snapshot(state['db'],'A')['kpi']=={}

def test_failure_preserves_cache_and_timestamp(monkeypatch):
    state={'user':'staff','db':copy.deepcopy(CLOUD),'synced_at':'08:00','current_shop':'A'}
    monkeypatch.setattr(sync,'fetch_data',Mock(side_effect=database.DatabaseError('offline')))
    assert not sync.refresh(state,True)
    assert state['db']==CLOUD and state['synced_at']=='08:00'
    assert state['sync_error']

def test_missing_user_ends_session(monkeypatch):
    state={'user':'removed','db':CLOUD}
    monkeypatch.setattr(sync,'fetch_data',lambda:CLOUD)
    assert not sync.refresh(state,True)
    assert state=={}

def test_refresh_interval(monkeypatch):
    state={'user':'staff','db':CLOUD};fetch=Mock(return_value=CLOUD)
    monkeypatch.setattr(sync,'fetch_data',fetch)
    clock=Mock(return_value=100.0);monkeypatch.setattr(sync.time,'monotonic',clock)
    assert sync.refresh(state)
    clock.return_value=110.;assert sync.refresh(state)
    assert fetch.call_count==1
    clock.return_value=131.;assert sync.refresh(state)
    assert fetch.call_count==2

def test_login_same_normalization_as_app():
    db={'users':{'Staff':{'password':'pass'}}}
    assert authenticate(db,' STAFF ','pass')
    assert authenticate(db,'STAFF','wrong') is None

def test_kpi_writes_exact_desktop_path(monkeypatch):
    import views.kpi as view
    fake=Mock(return_value=True);monkeypatch.setattr(view,'save',fake)
    record={'base':100,'short':20,'tgt':120,'sold':91}
    view.update_kpi_db('A','An',record)
    fake.assert_called_once_with('shops/A/kpi/emp/An',record)
