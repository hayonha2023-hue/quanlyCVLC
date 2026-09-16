"""Authentication against existing account records; no fallback credentials."""
import hmac

def authenticate(db, username, password):
    username = resolve_username(db, username)
    record = db.get('users', {}).get(username)
    if not isinstance(record, dict) or not password:
        return None
    stored = record.get('pass', record.get('password', record.get('mat_khau', '')))
    if not stored or not hmac.compare_digest(str(stored).encode(), password.encode()):
        return None
    return record

def roles(username, record):
    role = str(record.get('role','user')).lower()
    super_admin = role == 'super_admin' or (username.lower() == 'admin' and role == 'admin')
    return role in ('admin','super_admin'), super_admin


def resolve_username(db, username):
    wanted = str(username).strip().lower()
    matches = [key for key in db.get('users', {}) if str(key).strip().lower() == wanted]
    return matches[0] if len(matches) == 1 else wanted
