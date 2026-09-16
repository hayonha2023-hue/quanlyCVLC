"""Conditional Firebase write: never silently overwrite a concurrent update."""
import requests
from services.database import FIREBASE_URL, TIMEOUT, DatabaseError
from services.workflows import apply_schedule


def commit_schedule(user, shop, draft):
    try:
        response=requests.get(FIREBASE_URL,headers={'X-Firebase-ETag':'true'},timeout=TIMEOUT)
        response.raise_for_status()
        etag=response.headers.get('ETag')
        if not etag: raise DatabaseError('Máy chủ chưa cung cấp mốc dữ liệu để lưu an toàn. Chưa lưu lịch.')
        fresh=response.json()
        if not isinstance(fresh,dict): raise DatabaseError('Không đọc được dữ liệu để lưu lịch.')
        # Include fresh permissions, lock, fairness and all unrelated data in the transaction.
        updated=apply_schedule(fresh,user,shop,draft)
        saved=requests.put(FIREBASE_URL,json=updated,headers={'if-match':etag},timeout=TIMEOUT)
        if saved.status_code==412: raise DatabaseError('Có dữ liệu vừa thay đổi. Chưa lưu lịch; hãy làm mới và thử lại.')
        saved.raise_for_status()
        return updated
    except (requests.RequestException, TypeError) as exc:
        raise DatabaseError('Chưa xác nhận lưu lịch. Hãy làm mới dữ liệu để kiểm tra trước khi thử lại.') from exc
