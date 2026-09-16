"""Authentication against existing account records; no fallback credentials."""
import hmac

def authenticate(db, username, password):
    record = db.get('users', {}).get(username)
    if not isinstance(record, dict) or not password or not isinstance(record.get('pass'), (str, int)):
        return None
    if not hmac.compare_digest(str(record['pass']).encode(), password.encode()):
        return None
    return record

def roles(username, record):
    role = str(record.get('role','user')).lower()
    super_admin = role == 'super_admin' or (username.lower() == 'admin' and role == 'admin')
    return role in ('admin','super_admin'), super_admin
