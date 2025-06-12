from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID
from typing import List
from src.app import schemas, models, errors
from src.app.auth.dependencies import access_token_bearer, RoleChecker
from src.app.services import job_service, user_service, application_service as apps
from src.db.main import get_session


apps_router = APIRouter(
    tags=['Application']
)
who_can_apply = Depends(RoleChecker(["user"]))
general_roles = Depends(RoleChecker(["user", "admin", "employer"]))


async def parse_uuid_or_404(user_id: str) -> UUID:
    try:
        return UUID(user_id)
    except ValueError:
        raise errors.InvalidId()


@apps_router.get('/applications', status_code=status.HTTP_200_OK, response_model=List[schemas.Application], dependencies=[general_roles])
async def get_all_apps(session: AsyncSession = Depends(get_session), current_user: models.User = Depends(access_token_bearer)):
    applications = await apps.get_applications(session)

    return applications


@apps_router.get('/applications/list/{job_uid}', status_code=status.HTTP_200_OK, response_model=List[schemas.Application], dependencies=[general_roles])
async def get_job_applications(job_uid: str, session: AsyncSession = Depends(get_session), token_details=Depends(access_token_bearer)):

    job = await job_service.get_job_by_id(job_uid, session)

    if job is None:
        raise errors.JobNotFound()

    job_applications = await apps.get_job_applications(job.uid, session)

    return job_applications


@apps_router.post('/applications', status_code=status.HTTP_201_CREATED, response_model=schemas.Application, dependencies=[who_can_apply])
async def create_application(job_id: str, payload: schemas.ApplicationCreate, session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)):

    current_user = token_details.get('user')['user_uid']

    new_application = await apps.create_application(payload, current_user, job_id, session)

    return new_application


@apps_router.get('/applications/list', status_code=status.HTTP_200_OK, response_model=List[schemas.Application], dependencies=[general_roles])
async def get_user_applications(session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)):
    current_user = token_details.get('user')['user_uid']
 
    user_applications = await apps.get_user_applications(current_user, session)

    return user_applications

@apps_router.get('/applications/{application_uid}', status_code=status.HTTP_200_OK, response_model=schemas.Application, dependencies=[general_roles])
async def get_application(application_id: str, session: AsyncSession = Depends(get_session), token_details: dict=Depends(access_token_bearer)):
    application = await apps.get_application_by_id(application_id, session)

    if application is not None:
        return application
    
    else:
        raise errors.ApplicationNotFound()
    


@apps_router.put('/applications/{application_uid}', status_code=status.HTTP_202_ACCEPTED, response_model=schemas.Application, dependencies=[general_roles])
async def update_application(application_id: str, payload: schemas.ApplicationUpdate, session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)):

    application_to_update = await apps.get_application_by_id(application_id, session)

    #granting access to the endpoint
    current_user = token_details.get('user')['user_uid']
    if application_to_update.user_uid != UUID(current_user):
        raise errors.NotAuthorized()

    if application_to_update is not None:

        update_application = await apps.update_application(application_id, payload, session)

        return update_application
    
    else:
        raise errors.ApplicationNotFound()




@apps_router.delete('/applications/{application_uid}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[general_roles])
async def delete_application(application_id: str, session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)):

    apps_to_delete = await apps.get_application_by_id(application_id, session)
    if not apps_to_delete:
        raise errors.ApplicationNotFound()

    current_user = UUID(token_details.get('user')['user_uid'])

    if apps_to_delete.user_uid != current_user:
        raise errors.NotAuthorized()
    
    await apps.delete_application(application_id, session)


