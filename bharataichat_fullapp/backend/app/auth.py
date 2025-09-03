from datetime import datetime, timedelta
import os, jwt, hashlib
SECRET = os.environ.get('JWT_SECRET','changeme')
ALGO = 'HS256'

def create_access_token(sub: str, expires_minutes: int = 60):
    now = datetime.utcnow()
    payload = {'sub': sub, 'iat': now, 'exp': now + timedelta(minutes=expires_minutes)}
    return jwt.encode(payload, SECRET, algorithm=ALGO)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGO])
        return payload.get('sub')
    except Exception:
        return None

# simple password hash for demo (do not use in production)
def hash_password(pw: str):
    return hashlib.sha256(pw.encode()).hexdigest()
