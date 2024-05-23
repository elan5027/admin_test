from fastapi import FastAPI, Depends, HTTPException, status, Request, Response
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from models import Base
from schemas import AdminCreate, Admin, NewsCreate, News, AdminLogin
from crud import create_admin, authenticate_admin, create_news, get_news, get_news_by_id
from dependencies import get_db
from database import engine
from utils import create_session_token, verify_session_token
from typing import List
import uvicorn

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="mysecret")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

@app.post("/admin/join", response_model=Admin)
def join(admin: AdminCreate, db: Session = Depends(get_db)):
    db_admin = create_admin(db, admin)
    return db_admin

@app.post("/admin/login")
def login(admin: AdminLogin, request: Request, db: Session = Depends(get_db)):
    authenticated_admin = authenticate_admin(db, admin.admin_id, admin.password)
    if not authenticated_admin:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    session_token = create_session_token(admin.admin_id)
    request.session['session_token'] = session_token
    return {"message": "Login successful"}

@app.post("/logout")
def logout(request: Request):
    request.session.clear()
    return {"message": "Logout successful"}

@app.post("/news/write", response_model=News)
def write_news(news: NewsCreate, request: Request, db: Session = Depends(get_db)):
    session_token = request.session.get('session_token')
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    admin_id = verify_session_token(session_token)
    db_news = create_news(db, news, create_user=admin_id)
    return db_news

@app.get("/news", response_model=List[News])
def read_news(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    news_list = get_news(db, skip=skip, limit=limit)
    return news_list

@app.get("/news/{news_id}", response_model=News)
def read_news_by_id(news_id: int, db: Session = Depends(get_db)):
    db_news = get_news_by_id(db, news_id)
    if db_news is None:
        raise HTTPException(status_code=404, detail="News not found")
    return db_news


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
