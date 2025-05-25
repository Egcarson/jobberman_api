from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID
from typing import List
from src.app import schemas, models
from src.app.auth.dependencies import access_token_bearer, RoleChecker
from src.app.services import job_service, user_service, application_service as apps
from src.db.main import get_session


apps_router = APIRouter(
    tags=['Application']
)
who_can_apply = Depends(RoleChecker(["user"]))


async def parse_uuid_or_404(user_id: str) -> UUID:
    try:
        return UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid ID")


@apps_router.get('/applications', status_code=status.HTTP_200_OK, response_model=List[schemas.Application])
async def get_all_apps(session: AsyncSession = Depends(get_session), current_user: models.User = Depends(access_token_bearer)):
    applications = await apps.get_applications(session)

    return applications


@apps_router.get('/applications/list/{job_uid}', status_code=status.HTTP_200_OK, response_model=List[schemas.Application])
async def get_job_applications(job_uid: str, session: AsyncSession = Depends(get_session), token_details=Depends(access_token_bearer)):

    job = await job_service.get_job_by_id(job_uid, session)

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )

    job_applications = await apps.get_job_applications(job.uid, session)

    return job_applications


@apps_router.post('/applications', status_code=status.HTTP_201_CREATED, response_model=schemas.Application, dependencies=[who_can_apply])
async def create_application(job_id: str, payload: schemas.ApplicationCreate, session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)):

    current_user = token_details.get('user')['user_uid']

    new_application = await apps.create_application(payload, current_user, job_id, session)

    return new_application


@apps_router.get('/applications/list', status_code=status.HTTP_200_OK, response_model=List[schemas.Application])
async def get_user_applications(session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)):
    current_user = token_details.get('user')['user_uid']
 
    user_applications = await apps.get_user_applications(current_user, session)

    return user_applications

@apps_router.get('/applications/{application_uid}', status_code=status.HTTP_200_OK, response_model=schemas.Application)
async def get_application(application_id: str, session: AsyncSession = Depends(get_session), token_details: dict=Depends(access_token_bearer)):
    application = await apps.get_application_by_id(application_id, session)

    if application is not None:
        return application
    
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    


@apps_router.put('/applications/{application_uid}', status_code=status.HTTP_202_ACCEPTED, response_model=schemas.Application)
async def update_application(application_id: str, payload: schemas.ApplicationUpdate, session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)):

    application_to_update = await apps.get_application_by_id(application_id, session)

    #granting access to the endpoint
    current_user = token_details.get('user')['user_uid']
    if application_to_update.user_uid != UUID(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this endpoint!"
        )

    if application_to_update is not None:

        update_application = await apps.update_application(application_id, payload, session)

        return update_application
    
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )




@apps_router.delete('/jobs/{job_uid}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(job_uid: str, session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)):

    job = await job_service.get_job_by_id(job_uid, session)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    current_user = UUID(token_details.get('user')['user_uid'])

    if job.employer_uid != current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to perform this action!"
        )

    await job_service.delete_job(job_uid, session)
