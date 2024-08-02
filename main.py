import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from app.schemas import AdminCreate, Admin, NewsCreate, News, AdminLogin, NewsUpdate, PresignedUrlResponse
from app.crud import create_admin, authenticate_admin, create_news, get_news, get_news_by_id, get_admins, get_admin_by_id, update_news, get_all_news
from app.dependencies import get_db
from app.core.sqlalchemy import SQLAlchemyMiddleware
from typing import List
from app.auth import create_access_token, verify_token, oauth2_scheme


import uvicorn
import boto3

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
app = FastAPI()

app.add_middleware(
    SQLAlchemyMiddleware,
)

#Base.metadata.create_all(bind=engine)

s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION"),
)


@app.post("/admin/join", response_model=Admin)
def join(admin: AdminCreate, db: Session = Depends(get_db)):
    db_admin = create_admin(db, admin)
    return db_admin

@app.post("/admin/login", response_model=dict)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    admin = authenticate_admin(db, form_data.username, form_data.password)
    if not admin:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin.admin_id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/admin/list", response_model=List[Admin])
def list_admins(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    verify_token(token, db)
    admins = get_admins(db, skip=skip, limit=limit)
    return admins

@app.get("/admin/list/{admin_id}", response_model=Admin)
def read_admin(admin_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    verify_token(token, db)
    db_admin = get_admin_by_id(db, admin_id)
    if db_admin is None:
        raise HTTPException(status_code=404, detail="Admin not found")
    return db_admin

@app.post("/news/write", response_model=News)
def write_news(news: NewsCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    admin = verify_token(token, db)
    db_news = create_news(db, news, create_user=admin.admin_id)
    return db_news

@app.patch("/news/edit/{news_id}", response_model=News)
def edit_news(news_id: int, news_update: NewsUpdate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    verify_token(token, db)
    db_news = update_news(db, news_id, news_update)
    if db_news is None:
        raise HTTPException(status_code=404, detail="News not found")
    return db_news

@app.get("/news/page", response_model=List[News])
def read_news(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    verify_token(token, db)
    news_list = get_news(db, skip=skip, limit=limit)
    return news_list

@app.get("/news", response_model=List[News])
def read_all_news(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    verify_token(token, db)
    all_news = get_all_news(db)
    return all_news

@app.get("/news/details/{news_id}", response_model=News)
def read_news_by_id(news_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    verify_token(token, db)
    db_news = get_news_by_id(db, news_id)
    if db_news is None:
        raise HTTPException(status_code=404, detail="News not found")
    return db_news

def create_presigned_url(bucket_name: str, object_name: str, expiration=3600):
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name, 'Key': object_name},
                                                    ExpiresIn=expiration)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return response

@app.get("/presigned-url", response_model=PresignedUrlResponse)
def get_presigned_url(object_name: str, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    verify_token(token, db)
    bucket_name = os.getenv("AWS_S3_BUCKET")
    url = create_presigned_url(bucket_name, object_name)
    return {"url": url}