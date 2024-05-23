from sqlalchemy import Column, Integer, String, DateTime
from database import Base

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
    news_title = Column(String)
    create_user = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    status = Column(String)
    contents = Column(String)
    image_url = Column(String)
