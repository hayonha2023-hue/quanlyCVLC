"""Per-session refresh. A failed request never turns cached data into fresh data."""
import time
from datetime import datetime
from zoneinfo import ZoneInfo
from services.database import fetch_data, DatabaseError
from services.auth import roles
from services.app_data import DEFAULT_SHOP

INTERVAL = 30

def refresh(state, force=False):
    now=time.monotonic()
    if not force and now-state.get('_sync_attempt',-INTERVAL) < INTERVAL:
        return not bool(state.get('sync_error'))
    state['_sync_attempt']=now
    try:
        data=fetch_data()
    except DatabaseError as exc:
        state['sync_error']=str(exc)
        return False
    user=state.get('user','')
    record=data.get('users',{}).get(user)
    if not isinstance(record,dict):
        state.clear()
        return False
    state['db']=data
    state['is_admin'], state['is_super_admin']=roles(user,record)
    if not state['is_super_admin']:
        state['current_shop']=record.get('shop_id') or DEFAULT_SHOP
    state['sync_error']=''
    state['synced_at']=datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).strftime('%H:%M:%S %d/%m/%Y')
    return True
