from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc
from uuid import UUID
from src.app.models import User, Job, Application
from src.app import schemas
from src.app.auth.utils import hash_password


class UserService:

    async def get_all_users(self, session:AsyncSession):
        statement = select(User).order_by(desc(User.created_at))

        result = await session.exec(statement)

        return result.all()
    
    async def get_user(self, user_id: str, session:AsyncSession):
        statement = select(User).where(User.uid == user_id)

        result = await session.exec(statement)

        user = result.first()

        return user
    
    async def create_user(self, user_data: schemas.UserCreate, session: AsyncSession):
        user_data_dict = user_data.model_dump()
        
        new_user = User(
            **user_data_dict
        )

        new_user.hashed_password = hash_password(user_data_dict['hashed_password'])

        session.add(new_user)

        await session.commit()

        return new_user
    
    async def update_user(self, user_uid: str, user_data: schemas.UserUpdate, session: AsyncSession):
        user_to_update = await self.get_user(user_uid, session)

        if user_to_update is not None:
            user_data_dict = user_data.model_dump(exclude_unset=True)

            for k, v in user_data_dict.items():
                setattr(user_to_update, k, v)

                await session.commit()

            return user_to_update
        else:
            return None

    async def delete_user(self, user_uid: str, session: AsyncSession):
        user_to_delete = await self.get_user(user_uid, session)

        if user_to_delete is not None:
            await session.delete(user_to_delete)

            await session.commit()
        
        else:
            return None
        
    
    async def get_user_by_email(self, user_email: str, session:AsyncSession):
        statement = select(User).where(User.email_address == user_email)

        result = await session.exec(statement)

        user = result.first()

        return user if user is not None else None
    
    async def existing_user(self, user_email: str, session: AsyncSession):

        user = await self.get_user_by_email(user_email, session)
        return True if user is not None else False

class JobService():
    
    async def get_all_jobs(self, session: AsyncSession):
        statement = select(Job).order_by(desc(Job.created_at))

        result = await session.exec(statement)

        return result.all()
    
    async def get_job_by_id(self, job_uid: str, session: AsyncSession):
        statement = select(Job).where(Job.uid == job_uid)

        result = await session.exec(statement)

        return result.first()
    
    async def get_job_by_location(self, job_location: str, session: AsyncSession):
        statement = select(Job).where(Job.location == job_location)

        result = await session.exec(statement)

        return result.first()
    
    async def create_job(self, job_data: schemas.JobCreate, session: AsyncSession, user_uid: str):

        job_data_to_dict = job_data.model_dump()

        new_job = Job(
            **job_data_to_dict
        )
        
        new_job.employer_uid = user_uid

        session.add(new_job)
        await session.commit()

        return new_job
    
    async def get_employer_jobs(self, employer_uid: str, session: AsyncSession):
        statement = select(Job).where(Job.employer_uid == employer_uid).order_by(desc(Job.created_at))

        result = await session.exec(statement)

        return result.all()
    
    async def update_job(self, job_uid: str, payload: schemas.JobUpdate, session: AsyncSession):
        job_to_update = await self.get_job_by_id(job_uid, session)

        if job_to_update:
            job_dict_payload = payload.model_dump(exclude_unset=True)

            for k, v in job_dict_payload.items():
                setattr(job_to_update, k, v)

                await session.commit()

            return job_to_update
        else:
            return None
    
    async def delete_job(self, job_uid: str, session: AsyncSession):

        job_to_delete = await self.get_job_by_id(job_uid, session)
        
        if job_to_delete is not None:
            
            await session.delete(job_to_delete)
            await session.commit()
        
        else:
            return None

class ApplicationService():
    async def get_applications(self, session: AsyncSession):
        statement = select(Application).order_by(desc(Application.created_at))

        result = await session.exec(statement)

        return result.all()

    
    async def create_application(self, payload: schemas.ApplicationCreate, applicant_id: str, job_id: str, session: AsyncSession):

        application_data = payload.model_dump()

        new_apps = Application(
            **application_data,
            job_uid=UUID(job_id),
            user_uid=UUID(applicant_id)
            )

        session.add(new_apps)
        await session.commit()

        return new_apps

    async def get_job_applications(self, job_id: str, session: AsyncSession):
        statement = select(Application).where(Application.job_uid == job_id).order_by(desc(Application.created_at))

        result = await session.exec(statement)

        return result.all()
    
    async def get_user_applications(self, user_id: str, session: AsyncSession):
        statement = select(Application).where(Application.user_uid == user_id).order_by(desc(Application.created_at))

        result = await session.exec(statement)

        return result.all()

    async def get_application_by_id(self, application_id: str, session: AsyncSession):

        statement = select(Application).where(Application.uid == application_id).order_by(desc(Application.created_at))

        result = await session.exec(statement)

        return result.first()
    
    async def update_application(self, application_id: str, payload: schemas.ApplicationUpdate, session: AsyncSession):
        
        application = await self.get_application_by_id(application_id, session)

        application_to_update = payload.model_dump(exclude_unset=True)

        for k, v in application_to_update.items():
            setattr(application, k, v)

            await session.commit()
        
        return application
    
    async def delete_application(self, application_id: str, session: AsyncSession):

        app_to_delete = await self.get_application_by_id(application_id, session)

        if app_to_delete is not None:

            await session.delete(app_to_delete)
            await session.commit()

        else: 
            return None



user_service = UserService()
job_service = JobService()
application_service = ApplicationService()