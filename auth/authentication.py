import jwt
from datetime import datetime, timedelta
from django.conf import settings
from decouple import config

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = 'HS256'
EXPIRY_TIME = config('JWT_EXPIRY_TIME', default=15, cast=int)
ACCESS_TOKEN_LIFETIME = timedelta(minutes=EXPIRY_TIME)


def generate_jwt(user):
    payload = {
        'user_id': user.id,
        'exp': datetime.now() + ACCESS_TOKEN_LIFETIME,
        'iat': datetime.now(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_jwt(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
