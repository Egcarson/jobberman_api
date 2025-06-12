from fastapi import Request, status, HTTPException, Depends
from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from typing import Any, List
from src.app.auth.utils import verify_access_token
from src.db.redis import token_in_blocklist
from src.db.main import get_session
from src.app.services import user_service
from src.app import errors
from src.app.models import User

class AccessPass(HTTPBearer):
    def __init__(self, auto_error = True):
        super().__init__(auto_error=auto_error)
    
    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)

        token = creds.credentials

        token_data = verify_access_token(token)

        if not self.is_token_valid(token):
            raise errors.InvalidToken()
    
        jti = token_data.get('jti')
        if jti is None:
            raise errors.TokenExpired()
        
        if await token_in_blocklist(jti):
            raise errors.InvalidToken()
            # raise HTTPException(
            #     status_code=status.HTTP_403_FORBIDDEN,
            #     detail={
            #         "message": "Invalid token or user has been logged out",
            #         "resolution": "Please generate a new token or login again"
            #     }
            # )
        
        self.verify_token_data(token_data)
        
        return token_data
    
    def is_token_valid(self, token: str) -> bool:
        
        token_data = verify_access_token(token)

        return True if token_data is not None else False

    def verify_token_data(self, token_data):
        raise NotImplementedError("Please override this method in child classes")

class AccessTokenBearer(AccessPass):
    def verify_token_data(self, token_data: dict):

        if token_data and token_data.get("refresh"):
            raise errors.AccessToken
        
class RefreshTokenBearer(AccessPass):
    def verify_token_data(self, token_data: dict):

        if token_data and not token_data.get("refresh"):
            raise errors.RefreshToken()


async def get_current_user(token_details: dict = Depends(AccessTokenBearer()), session: AsyncSession = Depends(get_session)):
    user_data = token_details['user']['email']

    user = await user_service.get_user_by_email(user_data, session)

    return user

class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = [role.lower() for role in allowed_roles]

    def __call__(self, current_user: User = Depends(get_current_user)) -> Any:

        if not current_user.is_verified:
            raise errors.AccountNotVerified()
        
        user_role = current_user.role.lower()
        if user_role in self.allowed_roles:
            return True
        
        raise errors.RoleCheckAccess()

access_token_bearer = AccessTokenBearer()
refresh_token_bearer = RefreshTokenBearer()