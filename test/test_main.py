import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.main import app, get_db
from app.schemas import AdminCreate, AdminLogin, NewsCreate, NewsUpdate

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_module():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def test_admin_signup():
    response = client.post("/admin/join", json={
        "admin_id": "testadmin",
        "password": "Test@1234",
        "department": "TestDept",
        "position": "Tester",
        "name": "Test Admin",
        "email": "testadmin@example.com",
        "status": "ACTIVE"
    })
    assert response.status_code == 200
    assert response.json()["admin_id"] == "testadmin"

def test_admin_login():
    response = client.post("/admin/login", data={"username": "testadmin", "password": "Test@1234"})
    print(response)
    assert response.status_code == 200
    assert "access_token" in response.json()
    global access_token
    access_token = response.json()["access_token"]

def test_create_news():
    response = client.post("/news/write", json={
         "newsRequestKoDto": {
            "title": "모핑아이 MOU",
            "contents": "바미에듀 MOU관련 내용입니다.",
            "imageUrl": "https://example.com/image.jpg"
        },
        "newsRequestEnDto": {
            "title": "BAMIEDU MOU",
            "contents": "BAMIEDU MOU Contents.",
            "imageUrl": "https://example.com/image_en.jpg"
        },
        "status": "ACTIVE"
    }, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["newsRequestKoDto"]["title"] == "모핑아이 MOU"

def test_edit_news():
    response = client.patch("/news/edit/1", json={
        "newsRequestKoDto": {
            "title": "Updated 모핑아이 MOU",
            "contents": "Updated 바미에듀 MOU관련 내용입니다.",
            "imageUrl": "https://example.com/updated_image.jpg"
        },
        "newsRequestEnDto": {
            "title": "Updated BAMIEDU MOU",
            "contents": "Updated BAMIEDU MOU Contents.",
            "imageUrl": "https://example.com/updated_image_en.jpg"
        },
        "status": "ACTIVE"
    }, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["newsRequestKoDto"]["title"] == "Updated 모핑아이 MOU"

def test_read_news():
    response = client.get("/news", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_read_all_news():
    response = client.get("/news/page", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_read_news_by_id():
    response = client.get("/news/details/1", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["id"] == 1

def test_admin_list():
    response = client.get("/admin/list", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_admin_detail():
    response = client.get("/admin/list/1", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["id"] == 1

def test_get_presigned_url():
    response = client.get("/presigned-url", params={"object_name": "test_image.jpg"}, headers={"Authorization": f"Bearer {access_token}"})
    print("!!!", response)
    assert response.status_code == 200
    assert "url" in response.json()