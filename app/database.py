# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base

# #DATABASE_URL = "sqlite:///./test.db"
# DATABASE_URL = "postgresql+asyncpg://testuser:testpassword@localhost:5432/testdb"
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()

from contextvars import ContextVar, Token
from enum import Enum

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import Delete, Insert, Update


session_context: ContextVar[str] = ContextVar("session_context")


class EngineType(Enum):
    WRITER = "writer"
    READER = "reader"


def get_session_context() -> str:
    return session_context.get()


def set_session_context(session_id: str) -> Token:
    return session_context.set(session_id)


def reset_session_context(context: Token) -> None:
    session_context.reset(context)

database_url="postgresql+asyncpg://testuser:1234@localhost:5432/testdb"
def set_engines() -> dict:
    engine = create_async_engine(
        database_url,
        pool_size=20,
        echo=True,
        pool_pre_ping=True,
        max_overflow=10,
    )

    return {
        EngineType.WRITER: engine.execution_options(isolation_level="SERIALIZABLE"),
        EngineType.READER: engine,
    }


engines = set_engines()


class RoutingSession(Session):
    def get_bind(self, mapper=None, clause=None, **kw):
        if self._flushing or isinstance(clause, (Update, Delete, Insert)):
            return engines[EngineType.WRITER].sync_engine
        else:
            return engines[EngineType.READER].sync_engine


async_session_factory = async_sessionmaker(
    class_=AsyncSession,
    sync_session_class=RoutingSession,
    expire_on_commit=False,
)

session = async_scoped_session(
    session_factory=async_session_factory,
    scopefunc=get_session_context,
)
