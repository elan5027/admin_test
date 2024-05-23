from sqlalchemy.orm import Session
from app.models import Admin, News
from app.schemas import AdminCreate, NewsCreate, NewsUpdate, BaseModel
from passlib.context import CryptContext
from datetime import datetime, timezone

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_admin(db: Session, admin_id: str):
    return db.query(Admin).filter(Admin.admin_id == admin_id).first()

def get_admins(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Admin).offset(skip).limit(limit).all()

def get_admin_by_id(db: Session, admin_id: int):
    return db.query(Admin).filter(Admin.id == admin_id).first()

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
    admin = get_admin(db, admin_id)
    if not admin or not pwd_context.verify(password, admin.password):
        return None
    return admin

def create_news(db: Session, news: NewsCreate, create_user: str):
    db_news = News(
        newsRequestKoDto=news.newsRequestKoDto.model_dump(),
        newsRequestEnDto=news.newsRequestEnDto.model_dump(),
        status=news.status,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(db_news)
    db.commit()
    db.refresh(db_news)
    return db_news

def update_news(db: Session, news_id: int, news_update: NewsUpdate):
    db_news = get_news_by_id(db, news_id)
    if db_news is None:
        return None
    update_data = news_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_news, key, value)
    db_news.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_news)
    return db_news

def get_news(db: Session, skip: int = 0, limit: int = 10):
    return db.query(News).offset(skip).limit(limit).all()

def get_all_news(db: Session):
    return db.query(News).all()

def get_news_by_id(db: Session, news_id: int):
    return db.query(News).filter(News.id == news_id).first()
