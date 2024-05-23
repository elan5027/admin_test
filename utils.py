from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from fastapi import HTTPException

serializer = URLSafeTimedSerializer("mysecret")

def create_session_token(data: str) -> str:
    return serializer.dumps(data)

def verify_session_token(token: str, max_age: int = 3600) -> str:
    try:
        return serializer.loads(token, max_age=max_age)
    except (BadSignature, SignatureExpired):
        raise HTTPException(status_code=403, detail="Invalid or expired session token")
