from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
from uuid import UUID
from src.app import schemas, errors
from src.db.main import get_session
from src.app.services import user_service
from src.app.auth.dependencies import access_token_bearer
from src.app.auth.dependencies import RoleChecker


role_checker = Depends(RoleChecker(["user", "employer"]))

user_router = APIRouter(
    tags=["Users"]
)

# Dependency to handle parsing and validation of the UUID
async def parse_uuid_or_404(user_id: str) -> UUID:
    try:
        return UUID(user_id)
    except ValueError:
        raise errors.InvalidId()
    
@user_router.get("/users", status_code=status.HTTP_200_OK, response_model=List[schemas.User], dependencies=[role_checker])
async def get_all_users(session: AsyncSession = Depends(get_session), token_details=Depends(access_token_bearer)):
    users = await user_service.get_all_users(session)
    return users

@user_router.get("/users/{user_uid}", status_code=status.HTTP_200_OK, response_model=schemas.UserDetails)
async def get_user(user_uid: UUID = Depends(parse_uuid_or_404), session: AsyncSession = Depends(get_session), current_user=Depends(access_token_bearer)):

    user = await user_service.get_user(user_uid, session)

    if not user:
        raise errors.UserNotFound()
    
    return user


@user_router.put("/users/{user_uid}", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.User)
async def update_user(user_data: schemas.UserUpdate, user_uid: str, session: AsyncSession = Depends(get_session), token_details: dict =Depends(access_token_bearer)):

    user_to_update = await user_service.get_user(user_uid, session)

    if user_to_update is None:
        raise errors.UserNotFound()

    current_user = UUID(token_details.get('user')['user_uid'])

    if user_to_update.uid != current_user:
        raise errors.NotAuthorized()

    updated_user = await user_service.update_user(user_uid, user_data, session)

    return updated_user

@user_router.delete("/users/{user_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_uid:str, session: AsyncSession = Depends(get_session), token_details: dict=Depends(access_token_bearer)):
    
    user_to_delete = await user_service.get_user(user_uid, session)

    if user_to_delete is None:
        raise errors.UserNotFound()

    current_user = UUID(token_details.get('user')['user_uid'])

    if user_to_delete.uid != current_user:
        raise errors.NotAuthorized()
    
    await user_service.delete_user(user_uid, session)

    return {"User deleted successfully!"}

    