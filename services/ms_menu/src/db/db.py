import datetime
from typing import Annotated, AsyncGenerator

from config import settings
from sqlalchemy import DateTime, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

engine = create_async_engine(settings.DATABASE_URL, echo=True)

async_session_factory = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

created_at = Annotated[
    datetime.datetime,
    mapped_column(DateTime(timezone=False), server_default=func.now()),
]
updated_at = Annotated[
    datetime.datetime,
    mapped_column(DateTime(timezone=False), onupdate=func.now(), nullable=True),
]


class TimestampMixin:
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


class Base(DeclarativeBase):
    repr_cols_num = 3
    repr_cols = tuple()

    def __repr__(self):
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")
        return f"<{self.__class__.__name__} {','.join(cols)}>"


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session
