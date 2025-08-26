from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# Report Schemas
class ReportBase(BaseModel):
    filename: str

class Report(ReportBase):
    id: int
    created_at: datetime
    user_id: int

    class Config:
        orm_mode = True

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    name: str
    profile_picture: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    reports: List[Report] = []

    class Config:
        orm_mode = True

# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Analysis Schemas
class AnalysisRequest(BaseModel):
    query: str
    useLiveData: bool
