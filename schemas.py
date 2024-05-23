from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AdminBase(BaseModel):
    admin_id: str
    department: str
    position: str
    name: str
    email: str
    status: str

class AdminCreate(AdminBase):
    password: str

class Admin(AdminBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class AdminLogin(BaseModel):
    admin_id: str
    password: str

class NewsBase(BaseModel):
    news_title: str
    create_user: str
    status: str

class NewsCreate(NewsBase):
    contents: str
    image_url: str

class News(NewsBase):
    id: int
    created_at: datetime
    updated_at: datetime
    contents: Optional[str] = None
    image_url: Optional[str] = None

    class Config:
        orm_mode = True
