from fastapi import APIRouter, status, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import timedelta
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta, timezone
from src.db.main import get_session
from src.app.auth.utils import verify_password, create_access_token
from src.app import schemas, errors
from src.app.services import user_service
from src.app.auth.dependencies import refresh_token_bearer, access_token_bearer
from src.db.redis import add_token_to_blocklist
from src.app.auth.dependencies import get_current_user, RoleChecker
import logging


auth_router = APIRouter(
    tags=["Authentication"]
)

REFRESH_EXPIRY = 2

role_checker = RoleChecker(["admin", "user"])

@auth_router.post('/signup', status_code=status.HTTP_201_CREATED, response_model=schemas.User)
async def signup(user_data:schemas.UserCreate, session: AsyncSession = Depends(get_session)):

    email = user_data.email_address
    
    existing_user = await user_service.existing_user(email, session)
    
    if existing_user:
        raise errors.UserAlreadyExists()
    
    new_user = await user_service.create_user(user_data, session)

    return new_user

@auth_router.post('/login', status_code=status.HTTP_202_ACCEPTED)
async def login(login_data: schemas.LoginData, session: AsyncSession = Depends(get_session)):
    
    username = login_data.email_address
    password = login_data.password

    user = await user_service.get_user_by_email(username, session)

    if user is not None:

        validate_password = verify_password(password, user.hashed_password)

        if validate_password:
            access_token = create_access_token(
                user_data={
                    'email': user.email_address,
                    'user_uid': str(user.uid),
                    'role': user.role
                }
            )

            refresh_token = create_access_token(
                user_data={
                    'email': user.email_address,
                    'user_uid': str(user.uid)
                },
                refresh=True,
                expiry=timedelta(days=REFRESH_EXPIRY)
            )

            return JSONResponse(
                content={
                    'message': 'User logged in successfully',
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'user':{
                        'email': user.email_address,
                        'user_uid': str(user.uid)
                    }
                }
            )
    logging.error("user entered an invalid Password or Username")
    raise errors.InvalidEmailOrPassword()

@auth_router.get('/refresh_token', status_code=status.HTTP_200_OK)
async def get_new_access_token(token_details: dict = Depends(refresh_token_bearer)):

    expiry_time = token_details['exp']

    if datetime.fromtimestamp(expiry_time, tz=timezone.utc) > datetime.now(timezone.utc):
        new_access_token = create_access_token(
            user_data=token_details['user']
        )
        return JSONResponse(
            content={
                "access_token": new_access_token
            }
        )
    
    raise errors.InvalidToken()

@auth_router.get('/me')
async def get_current_user(user = Depends(get_current_user), _: bool = Depends(role_checker)):
    return user

@auth_router.get('/logout', status_code=status.HTTP_200_OK)
async def logout(token_details: dict=Depends(access_token_bearer)):

    jti = token_details['jti']

    await add_token_to_blocklist(jti)

    return JSONResponse(
        content="Logged out successfully!",
        status_code=status.HTTP_200_OK
    )