import uuid
import jwt
import logging
from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone
from src.config import Config

passwd_context = CryptContext(
    schemes=['bcrypt']
)


ACCESS_TOKEN_EXPIRY = 2

def hash_password(password: str) -> str:
    return passwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return passwd_context.verify(password, hashed_password)

def create_access_token(user_data: dict, expiry: timedelta = None, refresh: bool = False):
    payload = {}

    payload['user'] = user_data
    payload['exp'] = datetime.now() + (expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRY))
    payload['jti'] = str(uuid.uuid4())
    payload['refresh'] = refresh
    
    token = jwt.encode(
        payload=payload,
        key=Config.JWT_SECRET,
        algorithm=Config.JWT_ALGORITHM
    )
    
    return token

def verify_access_token(token: str) -> dict:
    try:
        token_data = jwt.decode(
            jwt=token,
            key=Config.JWT_SECRET,
            algorithms=[Config.JWT_ALGORITHM]
        )

        if 'jti' not in token_data:
            raise KeyError("Token does not contain 'jti' field.")
        
        return token_data
    except jwt.ExpiredSignatureError as e:
        # Return the expired token exception
        logging.warning("Token has expired.")
        return {"error": str(e)}

    except jwt.PyJWKError as e:
        logging.exception(e)
        return None


