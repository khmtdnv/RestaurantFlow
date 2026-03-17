from datetime import datetime
from decimal import Decimal
from typing import Annotated

from config import settings
from sqlalchemy import Integer, Numeric, func
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

engine = create_async_engine(settings.DATABASE_URL, echo=True)

async_session_factory = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
numeric_price = Annotated[Decimal, mapped_column(Numeric(10, 2), nullable=False)]
created_at = Annotated[datetime, mapped_column(server_default=func.now())]
updated_at = Annotated[
    datetime,
    mapped_column(server_default=func.now(), onupdate=func.now()),
]
id_pk = Annotated[int, mapped_column(Integer, primary_key=True, autoincrement=True)]


class TimestampMixin:
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    repr_cols_num = 3
    repr_cols = tuple()

    def __repr__(self):
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")
        return f"<{self.__class__.__name__} {','.join(cols)}>"
