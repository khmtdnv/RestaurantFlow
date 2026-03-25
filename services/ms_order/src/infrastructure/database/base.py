from datetime import datetime
from decimal import Decimal
from typing import Annotated

from sqlalchemy import DateTime, Integer, MetaData, Numeric, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

id_pk = Annotated[int, mapped_column(Integer, primary_key=True, autoincrement=True)]
numeric_price = Annotated[Decimal, mapped_column(Numeric(10, 2), nullable=False)]


class TimestampMixin:
    """Base class for models with timestamp."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        sort_order=999,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        sort_order=1000,
    )


# Шаблоны именования для всех типов ограничений и индексов
POSTGRES_NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=POSTGRES_NAMING_CONVENTION)


class Base(DeclarativeBase):
    """Базовый класс для всех ORM моделей."""

    metadata = metadata
    __repr_attrs__: list[str] = []

    def __repr__(self) -> str:
        attrs = ", ".join(
            f"{attr}={getattr(self, attr)!r}" for attr in self.__repr_attrs__ if hasattr(self, attr)
        )
        return f"<{self.__class__.__name__}({attrs})>"
