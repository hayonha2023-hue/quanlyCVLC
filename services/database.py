"""Firebase transport: explicit failures, bounded waits, cache after server success."""
import copy
from urllib.parse import quote
import requests
import streamlit as st

FIREBASE_URL = 'https://htcv-5c857-default-rtdb.firebaseio.com/htcv.json'
TIMEOUT = (5, 15)

class DatabaseError(RuntimeError):
    pass

def request(method, path='', data=None):
    suffix = '/'.join(quote(part, safe='') for part in path.strip('/').split('/'))
    url = FIREBASE_URL[:-5] + ('/' + suffix if suffix else '') + '.json'
    try:
        response = requests.request(method, url, json=data, timeout=TIMEOUT)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as exc:
        raise DatabaseError('Không thể đồng bộ dữ liệu. Kiểm tra kết nối hoặc quyền truy cập rồi thử lại.') from exc

def fetch_data():
    data = request('GET') or {}
    if not isinstance(data, dict):
        raise DatabaseError('Dữ liệu máy chủ không đúng định dạng.')
    return data

def change_cache(db, path, value, method):
    result = copy.deepcopy(db)
    parts = path.strip('/').split('/') if path else []
    node = result
    for part in parts[:-1]:
        if not isinstance(node.get(part), dict): node[part] = {}
        node = node[part]
    if not parts:
        if method == 'PATCH': result.update(copy.deepcopy(value))
        else: result = copy.deepcopy(value)
    elif method == 'DELETE': node.pop(parts[-1], None)
    elif method == 'PATCH':
        if not isinstance(node.get(parts[-1]), dict): node[parts[-1]] = {}
        node[parts[-1]].update(copy.deepcopy(value))
    else: node[parts[-1]] = copy.deepcopy(value)
    return result

def save(path, value=None, method=None):
    method = method or ('PATCH' if isinstance(value, dict) else 'PUT')
    try:
        request(method, path, value)
    except DatabaseError as exc:
        st.error(str(exc))
        st.stop()  # Never continue to a caller's success toast after a failed write.
    st.session_state.db = change_cache(st.session_state.get('db', {}), path, value, method)
    return True

def shop_path(shop, path=''):
    prefix = '' if shop == 'Shop Chính (Mặc định)' else 'shops/' + shop
    return '/'.join(p for p in (prefix, path) if p)
