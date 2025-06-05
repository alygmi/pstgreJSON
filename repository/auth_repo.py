from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "rahasia_super_aman"
ALGORITHM = "HS256"
EXPIRE_MINUTES = 60

def generate_token(data: dict)->str:
    expire = datetime.utcnow() + timedelta(minutes=EXPIRE_MINUTES)
    payload = {
        **data,
        "iat": datetime.utcnow(),
        "exp": expire
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)