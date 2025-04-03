from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    first_name: str
    last_name: str
    user_name: str
    email_address: EmailStr
    phone_number: str
    gender: str
    
class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    pass

class User(UserBase):
    user_id: int
    date_joined: datetime
