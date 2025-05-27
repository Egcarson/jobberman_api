from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
import uuid
# from enum import Enum


# class UserRoles(str, Enum):
#     ADMIN = "admin"
#     USER = "user"
#     EMPLOYER = "employer"

class UserBase(BaseModel):
    first_name: str
    last_name: str
    username: str
    email_address: EmailStr
    role: str = "user"
    phone_number: str
    gender: str
    
class UserCreate(UserBase):
    hashed_password: str = Field(min_length=8)

class UserUpdate(UserBase):
    pass

class User(UserBase):
    uid: uuid.UUID
    created_at: datetime
    updated_at:datetime

# class Username(BaseModel):
#     username: str = Optional
#     email_address: EmailStr = Optional

class LoginData(BaseModel):
    email_address: EmailStr
    password: str


class JobBase(BaseModel):
    title: str
    description: str
    location: str
    salary: str
    is_active: bool =  False

class JobCreate(JobBase):
    pass

class JobUpdate(JobBase):
    pass

class Job(JobBase):
    uid: uuid.UUID 
    employer_uid: uuid.UUID
    created_at: datetime

class ApplicationCreate(BaseModel):
    cover_letter: str

class ApplicationUpdate(ApplicationCreate):
    pass

class Application(BaseModel):
    uid: uuid.UUID
    cover_letter: str 
    user_uid: uuid.UUID
    job_uid: uuid.UUID
    created_at: datetime 


class UserDetails(User):
    job: List[Job]
    application: List[Application]


class JobDetails(Job):
    application: List[Application]