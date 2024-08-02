from typing import Generator
from app.database import session

def get_db() -> Generator:
    db = session()
    try:
        yield db
    finally:
        db.close()
