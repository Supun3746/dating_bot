from asyncio import current_task

from sqlalchemy.ext.asyncio import (
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

from config import settings


class DatabaseHelper:
    def __init__(self, url: str, echo: bool = False):
        self.engine = create_async_engine(
            url=url,
            echo=echo,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )


db = DatabaseHelper(url=settings.DB_URL)


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(unique=True)
    user_nick: Mapped[str | None] = mapped_column(unique=True)
    name: Mapped[str]
    age: Mapped[int]
    find_gender: Mapped[bool]
    description: Mapped[str]
    photo: Mapped[str]
    photo_embedding: Mapped[str]


class Men(Base):
    __tablename__ = "men"


class Women(Base):
    __tablename__ = "women"


async def create_table():
    async with db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
