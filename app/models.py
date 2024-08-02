from sqlalchemy import Column, Integer, String, DateTime, JSON

from typing import Any
from sqlalchemy.ext.declarative import as_declarative


@as_declarative()
class Base:
    id: Any
    __name__: str


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(String, unique=True, index=True)
    password = Column(String)
    department = Column(String)
    position = Column(String)
    name = Column(String)
    email = Column(String)
    status = Column(String)
    created_at = Column(DateTime)
    

class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    newsRequestKoDto = Column(JSON)
    newsRequestEnDto = Column(JSON)
    status = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
