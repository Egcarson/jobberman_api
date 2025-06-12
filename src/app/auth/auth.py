from fastapi import APIRouter, status, Depends, HTTPException, BackgroundTasks
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import timedelta
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta, timezone
from src.db.main import get_session
from src.app.auth.utils import verify_password, create_access_token, create_url_safe_token, decode_url_safe_token, hash_password
from src.app import schemas, errors
from src.app.services import user_service
from src.app.auth.dependencies import refresh_token_bearer, access_token_bearer
from src.db.redis import add_token_to_blocklist
from src.app.auth.dependencies import get_current_user, RoleChecker
import logging
from src.app.mail import mail, create_message
from src.config import Config
from src.celery_tasks import send_email as celery_worker


auth_router = APIRouter(
    tags=["Authentication"]
)

REFRESH_EXPIRY = 2

role_checker = RoleChecker(["admin", "user"])

@auth_router.post('/send_email')
async def send_email(emails: schemas.EmailModel):

    emails = emails.addresses

    html = "<h1>Welcome to jobberman app<h1>"

    subject="Testing celery"

    email_list = [emails]

    celery_worker.delay(email_list, subject, html)

    return {"message": "email sent successfully!"}

@auth_router.post('/signup', status_code=status.HTTP_201_CREATED)
async def signup(user_data: schemas.UserCreate, bg_tasks: BackgroundTasks, session: AsyncSession = Depends(get_session)):
    """"
    Create use account using email_address, username, first_name, last_name
    params:
        user_data: schemas.UserCreate
    """

    email = user_data.email_address

    existing_user = await user_service.existing_user(email, session)

    if existing_user:
        raise errors.UserAlreadyExists()

    new_user = await user_service.create_user(user_data, session)

    token = create_url_safe_token({"email": email})

    link = f"http://{Config.DOMAIN}/api/v1.0/auth/verify_email/{token}"

    html_message =f"""
    <h1>Verify your Email Address</h1>
    <p>Please click on the <a href="{link}">link</a> to veify your account</p>
    """
    emails = [email]

    subject = "Verify your email"

    celery_worker.delay(emails, subject, html_message)

    return {
        "message": "Account has been created successfuly! Please check your email to verify your account.",
        "user": new_user
    }


@auth_router.get('/auth/verify_email/{token}', status_code=status.HTTP_200_OK)
async def verify_user_account(token: str, session: AsyncSession = Depends(get_session)):

    token_data = decode_url_safe_token(token)

    if not token_data:
        raise errors.InvalidToken()

    user_email = token_data.get('email')

    if user_email:
        user = await user_service.get_user_by_email(user_email, session)

        if not user:
            raise errors.UserNotFound()
        
        await user_service.update_user_info(user, {"is_verified": True}, session)

        return JSONResponse(
            content={"message": "Account has been verified successfully!"},
            status_code=status.HTTP_200_OK
        )
    
    return JSONResponse(
        content={"message": "An error occured during verification!"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


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
                    'user': {
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
async def get_current_user(user=Depends(get_current_user), _: bool = Depends(role_checker)):
    return user


@auth_router.get('/logout', status_code=status.HTTP_200_OK)
async def logout(token_details: dict = Depends(access_token_bearer)):

    jti = token_details['jti']

    await add_token_to_blocklist(jti)

    return JSONResponse(
        content="Logged out successfully!",
        status_code=status.HTTP_200_OK
    )


@auth_router.post('/password-reset-request')
async def password_reset_request(email_data: schemas.PasswordResetRequest):
    
    email = email_data.email_address

    token = create_url_safe_token({"email": email})

    link = f"http://{Config.DOMAIN}/api/v1.0/auth/confirm-password-reset/{token}"

    html_message =f"""
    <h1>Reset your Password</h1>
    <p>Please click on the <a href="{link}">link</a> to reset your password</p>
    """
    
    message = create_message(
        recipients=[email],
        subject="Password reset",
        body=html_message
    )

    mail.send_message(message)

    return JSONResponse(
        content={"message": "Please check your email for instructions to reset your password."},
        status_code=status.HTTP_200_OK
    )

@auth_router.post('/auth/confirm-password-reset/{token}', status_code=status.HTTP_200_OK)
async def confirm_password_reset(passwd_data: schemas.ConfirmPasswordReset, token: str, session: AsyncSession = Depends(get_session)):

    new_password = passwd_data.new_password
    confirm_password = passwd_data.confirm_password

    if confirm_password != new_password:
        raise HTTPException(
            detail={"message": "Password does not match"},
            status_code=status.HTTP_403_FORBIDDEN
        )

    token_data = decode_url_safe_token(token)

    if not token_data:
        raise errors.InvalidToken()

    user_email = token_data.get('email')

    if user_email:
        user = await user_service.get_user_by_email(user_email, session)

        if not user:
            raise errors.UserNotFound()
        
        hashed_password = hash_password(new_password)
        
        await user_service.update_user_info(user, {"hashed_password": hashed_password}, session)

        return JSONResponse(
            content={"message": "Your password has been changed successfully!"},
            status_code=status.HTTP_200_OK
        )
    
    return JSONResponse(
        content={"message": "An error occured during verification!"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )