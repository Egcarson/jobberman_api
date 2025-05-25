from sqlmodel import SQLModel, Column, Field, ForeignKey, Relationship, Text
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy import Enum as PgEnum, UniqueConstraint
from datetime import datetime
from typing import List, Optional
import uuid


class User(SQLModel, table=True):
    __tablename__ = "users"

    uid: uuid.UUID = Field(default_factory=uuid.uuid4, sa_column=Column(pg.UUID(as_uuid=True), nullable=False, primary_key=True))
    username: str
    email_address: str
    first_name: str
    last_name: str
    hashed_password: str = Field(exclude=True)
    phone_number: str
    gender: str
    role: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, server_default="user"))
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    jobs: List["Job"] = Relationship(back_populates="employer")
    applications: List["Application"] = Relationship(back_populates="user")

    def __repr__(self):
        return f"<User id={self.uid}, username={self.username}, email={self.email_address}>"

class Job(SQLModel, table=True):
    __tablename__ = "jobs"

    uid: uuid.UUID = Field(default_factory=uuid.uuid4, sa_column=Column(pg.UUID(as_uuid=True), nullable=False, primary_key=True))
    title: str
    description: str = Field(sa_column=Column(Text, nullable=False))
    location: str
    salary: str
    is_active: bool = Field(default=False)
    employer_uid: uuid.UUID = Field(sa_column=Column(pg.UUID(as_uuid=True), ForeignKey("users.uid"), nullable=False))
    created_at: datetime = Field(default_factory=datetime.now, sa_column=Column(pg.TIMESTAMP(timezone=True), nullable=False))

    employer: Optional["User"] = Relationship(back_populates="jobs")
    applications: List["Application"] = Relationship(back_populates="jobs")


class Application(SQLModel, table=True):
    __tablename__ = "applications"

    uid: uuid.UUID = Field(default_factory=uuid.uuid4, sa_column=Column(pg.UUID(as_uuid=True), nullable=False, primary_key=True))
    job_uid: uuid.UUID = Field(sa_column=Column(pg.UUID(as_uuid=True), ForeignKey("jobs.uid"), nullable=False))
    user_uid: uuid.UUID = Field(sa_column=Column(pg.UUID(as_uuid=True), ForeignKey("users.uid"), nullable=False))
    cover_letter: str = Field(sa_column=Column(Text, nullable=False))
    created_at: datetime = Field(default_factory=datetime.now, sa_column=Column(pg.TIMESTAMP(timezone=True), nullable=False))

    jobs: Optional["Job"] = Relationship(back_populates="applications")
    user: Optional["User"] = Relationship(back_populates="applications")

    __table_args__ = (UniqueConstraint("job_uid", "user_uid", name="uq_job_seeker"),)
