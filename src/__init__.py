from fastapi import FastAPI, status
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from src.app.auth import auth
from src.db.main import init_db
from src.app.errors import (
    InvalidToken,
    TokenExpired,
    AccessToken,
    RefreshToken,
    RoleCheckAccess,
    UserAlreadyExists,
    UserNotFound,
    InvalidEmailOrPassword,
    InvalidId,
    NotAuthorized,
    JobNotFound,
    ApplicationNotFound,
    create_exception_handler
)
from src.app.router import users, jobs, application


@asynccontextmanager
async def life_span(app: FastAPI):
    print(f"sever is starting ..........")
    await init_db()
    yield
    print(f"sever is shutting down ..........")
    print(f"sever has been stopped")

version = "v1.0"

app = FastAPI(
    title="Jobberman API",
    description="REST API for job search web app",
    version=version,
    lifespan=life_span
)

#exception block

#TokenExpired
app.add_exception_handler(
    InvalidToken,
    create_exception_handler(
        status_code=status.HTTP_401_UNAUTHORIZED,
        initial_detail={
            "message": "Invalid or expired token",
            "resolution": "Please generate a new token or login again",
            "error_code": "invalid_token"
        }
    )
)
# TokenExpired
app.add_exception_handler(
    TokenExpired,
    create_exception_handler(
        status_code=status.HTTP_400_BAD_REQUEST,
        initial_detail={
            "message": "Token has expired or you've been logged out",
            "resolution": "Please generate a new token or login again",
            "error_code": "token_expired"
        }
    )
)
# AccessToken
app.add_exception_handler(
    AccessToken,
    create_exception_handler(
        status_code=status.HTTP_401_UNAUTHORIZED,
        initial_detail={
            "message": "Please provide a valid access token",
            "resolution": "Please generate an access token",
            "error_code": "access_token_required"
        }
    )
)
# RefreshToken
app.add_exception_handler(
    RefreshToken,
    create_exception_handler(
        status_code=status.HTTP_401_UNAUTHORIZED,
        initial_detail={
            "message": "Please provide a valid refresh token",
            "resolution": "Please get a new refresh token",
            "error_code": "refresh_token_required"
        }
    )
)
# RoleCheckAccess
app.add_exception_handler(
    RoleCheckAccess,
    create_exception_handler(
        status_code=status.HTTP_401_UNAUTHORIZED,
        initial_detail={
            "message": "You are not authorized to complete this action!",
            "error_code": "unauthorized_user_role"
        }
    )
)
# UserAlreadyExists
app.add_exception_handler(
    UserAlreadyExists,
    create_exception_handler(
        status_code=status.HTTP_400_BAD_REQUEST,
        initial_detail={
            "message": "User already exists!",
            "resolution": "Signup with a different email or proceed to login",
            "error_code": "user_exists"
        }
    )
)
# UserNotFound
app.add_exception_handler(
    UserNotFound,
    create_exception_handler(
        status_code=status.HTTP_404_NOT_FOUND,
        initial_detail={
            "message": "User not found",
            "resolution": "The user does not exist or has been removed",
            "error_code": "user_not_found"
        }
    )
)
# InvalidEmailOrPassword
app.add_exception_handler(
    InvalidEmailOrPassword,
    create_exception_handler(
        status_code=status.HTTP_400_BAD_REQUEST,
        initial_detail={
            "message": "Invalid login credentials",
            "resolution": "Please provide a valid email or password",
            "error_code": "invalid_login_details"
        }
    )
)
# InvalidId
app.add_exception_handler(
    InvalidId,
    create_exception_handler(
        status_code=status.HTTP_400_BAD_REQUEST,
        initial_detail={
            "message": "This is not a valid UUID number!",
            "resolution": "Please provide a valid id",
            "error_code": "invalid_uid"
        }
    )
)
# NotAuthorized
app.add_exception_handler(
    NotAuthorized,
    create_exception_handler(
        status_code=status.HTTP_401_UNAUTHORIZED,
        initial_detail={
            "message": "You do not have the permission to continue!",
            "error_code": "unauthorized_user"
        }
    )
)
# JobNotFound
app.add_exception_handler(
    JobNotFound,
    create_exception_handler(
        status_code=status.HTTP_404_NOT_FOUND,
        initial_detail={
            "message": "Job not found",
            "error_code": "job_not_found"
        }
    )
)
# ApplicationNotFound
app.add_exception_handler(
    ApplicationNotFound,
    create_exception_handler(
        status_code=status.HTTP_404_NOT_FOUND,
        initial_detail={
            "message": "Application not found",
            "error_code": "application_not_found"
        }
    )
)

#server exception handler
@app.exception_handler(500)
async def internal_server_error(request, exc):
    return JSONResponse(
        content={
            "message": "Ooops!............something went wrong",
            "error_code": "server_error"
        },
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

app.include_router(auth.auth_router, prefix=f'/api/{version}')
app.include_router(users.user_router, prefix=f'/api/{version}')
app.include_router(jobs.job_router, prefix=f'/api/{version}')
app.include_router(application.apps_router, prefix=f'/api/{version}')


@app.get('/')
async def root():
    return {"message": "Jobberman API"}
