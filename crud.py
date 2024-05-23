from sqlalchemy.orm import Session
from models import Admin, News
from schemas import AdminCreate, NewsCreate
from passlib.context import CryptContext
from datetime import datetime, timezone

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_admin(db: Session, admin_id: str):
    return db.query(Admin).filter(Admin.admin_id == admin_id).first()

def create_admin(db: Session, admin: AdminCreate):
    hashed_password = pwd_context.hash(admin.password)
    db_admin = Admin(
        admin_id=admin.admin_id,
        password=hashed_password,
        department=admin.department,
        position=admin.position,
        name=admin.name,
        email=admin.email,
        status=admin.status,
        created_at=datetime.now(timezone.utc)
        
    )
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin

def authenticate_admin(db: Session, admin_id: str, password: str):
    print(admin_id, password)
    admin = get_admin(db, admin_id)
    if not admin or not pwd_context.verify(password, admin.password):
        return None
    return admin

def create_news(db: Session, news: NewsCreate, create_user: str):
    db_news = News(
        news_title=news.news_title,
        create_user=create_user,
        contents=news.contents,
        image_url=news.image_url,
        status=news.status,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(db_news)
    db.commit()
    db.refresh(db_news)
    return db_news

def get_news(db: Session, skip: int = 0, limit: int = 10):
    return db.query(News).offset(skip).limit(limit).all()

def get_news_by_id(db: Session, news_id: int):
    return db.query(News).filter(News.id == news_id).first()
