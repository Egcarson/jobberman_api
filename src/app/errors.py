from typing import Any, Callable
from fastapi.requests import Request
from fastapi.responses import JSONResponse


class ExceptionSystemManager(Exception):
    """Default home for all API errors"""
    pass

class InvalidToken(ExceptionSystemManager):
    """Invalid token or expired token"""
    pass

class TokenExpired(ExceptionSystemManager):
    """Token expired or user have been logged out"""
    pass

class AccessToken(ExceptionSystemManager):
    """Please provide an access token"""
    pass

class RefreshToken(ExceptionSystemManager):
    """Please provide a refresh token"""
    pass

class RoleCheckAccess(ExceptionSystemManager):
    """You are not allowed to access this endpoint. Action aborted!"""
    pass

class UserAlreadyExists(ExceptionSystemManager):
    """User already exists. Please proceed to Login"""
    pass

class UserNotFound(ExceptionSystemManager):
    """User does not exist!"""
    pass

class InvalidEmailOrPassword(ExceptionSystemManager):
    """Invalid email or password"""
    pass

class InvalidId(ExceptionSystemManager):
    """Invalid ID"""
    pass

class NotAuthorized(ExceptionSystemManager):
    """You are not authorized to access this endpoint."""
    pass

class JobNotFound(ExceptionSystemManager):
    """Job does not exist!"""
    pass

class ApplicationNotFound(ExceptionSystemManager):
    """Application does not exist!"""
    pass


def create_exception_handler(status_code: int, initial_detail: Any) -> Callable[[Request, Exception], JSONResponse]:

    async def exception_handler(request: Request, exception: ExceptionSystemManager):

        return JSONResponse(
            content=initial_detail,
            status_code=status_code
        )
    
    return exception_handler