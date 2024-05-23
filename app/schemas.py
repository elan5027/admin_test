from pydantic import BaseModel, ConfigDict
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

    model_config = ConfigDict(from_attributes=True)

class AdminLogin(BaseModel):
    admin_id: str
    password: str

class NewsRequestKoDto(BaseModel):
    title: str
    contents: str
    imageUrl: str

class NewsRequestEnDto(BaseModel):
    title: str
    contents: str
    imageUrl: str

class NewsBase(BaseModel):
    newsRequestKoDto: NewsRequestKoDto
    newsRequestEnDto: NewsRequestEnDto
    status: str

class NewsCreate(NewsBase):
    pass

class NewsUpdate(BaseModel):
    newsRequestKoDto: Optional[NewsRequestKoDto]
    newsRequestEnDto: Optional[NewsRequestEnDto]
    status: Optional[str]

class News(NewsBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PresignedUrlResponse(BaseModel):
    url: str
