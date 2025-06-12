from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID
from typing import List
from src.app import schemas, models, errors
from src.app.auth.dependencies import access_token_bearer, RoleChecker
from src.app.services import job_service, user_service
from src.db.main import get_session


job_router = APIRouter(
    tags=['Jobs Route']
)
job_listing_role = Depends(RoleChecker(["employer", "admin"]))
general_roles = Depends(RoleChecker(["employer", "admin", "user"]))


async def parse_uuid_or_404(user_id: str) -> UUID:
    try:
        return UUID(user_id)
    except ValueError:
        raise errors.InvalidId()


@job_router.get('/jobs', status_code=status.HTTP_200_OK, response_model=List[schemas.Job], dependencies=[general_roles])
async def get_all_jobs(session: AsyncSession = Depends(get_session), current_user: models.User = Depends(access_token_bearer)):
    jobs = await job_service.get_all_jobs(session)

    return jobs


@job_router.get('/jobs/{job_uid}', status_code=status.HTTP_200_OK, response_model=schemas.JobDetails, dependencies=[general_roles])
async def get_job(job_uid: str, session: AsyncSession = Depends(get_session), token_details=Depends(access_token_bearer)):

    job = await job_service.get_job_by_id(job_uid, session)

    if job is not None:
        return job

    raise errors.JobNotFound()

@job_router.post('/jobs', status_code=status.HTTP_201_CREATED, response_model=schemas.Job, dependencies=[job_listing_role])
async def create_job(payload: schemas.JobCreate, session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)):

    current_user = token_details.get('user')['user_uid']

    new_job = await job_service.create_job(payload, session, current_user)

    return new_job

@job_router.get('/jobs/employer_listed_jobs/{user_uid}', status_code=status.HTTP_200_OK, dependencies=[general_roles])
async def get_employer_jobs(user_uid: str, session: AsyncSession = Depends(get_session), token_details: dict=Depends(access_token_bearer)):
    current_user = token_details.get('user')['user_uid']
    if user_uid != current_user:
        raise errors.NotAuthorized()
    
    jobs = await job_service.get_employer_jobs(current_user, session)

    return jobs

# @job_router.get('/employer_jobs', status_code=status.HTTP_200_OK)
# async def get_employer_jobs(session: AsyncSession = Depends(get_session), token_details: dict=Depends(access_token_bearer)):
#     current_user = token_details.get('user')['user_uid']
#     if not current_user:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You are not allowed to perform this action"
#         )

#     jobs = await job_service.get_employer_jobs(current_user, session)

#     return jobs

@job_router.put('/jobs/{job_uid}', status_code=status.HTTP_202_ACCEPTED, response_model=schemas.Job, dependencies=[general_roles])
async def update_job(job_uid: str, payload: schemas.JobUpdate, session: AsyncSession = Depends(get_session), token_details: dict=Depends(access_token_bearer)):

    job = await job_service.get_job_by_id(job_uid, session)
    if not job:
        raise errors.JobNotFound()

    current_user = UUID(token_details.get('user')['user_uid'])

    if job.employer_uid != current_user:
        raise errors.NotAuthorized()
    
    updated_job = await job_service.update_job(job_uid, payload, session)
    
    return updated_job

@job_router.delete('/jobs/{job_uid}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[general_roles])
async def delete_job(job_uid: str, session: AsyncSession = Depends(get_session), token_details: dict=Depends(access_token_bearer)):

    job = await job_service.get_job_by_id(job_uid, session)
    if not job:
        raise errors.JobNotFound()

    current_user = UUID(token_details.get('user')['user_uid'])

    if job.employer_uid != current_user:
        raise errors.NotAuthorized()
    
    await job_service.delete_job(job_uid, session)