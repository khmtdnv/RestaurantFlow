from datetime import datetime
from decimal import Decimal
from typing import Annotated

from sqlalchemy import DateTime, Integer, Numeric, func
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


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    __repr_attrs__: list[str] = []

    def __repr__(self) -> str:
        attrs = ", ".join(
            f"{attr}={getattr(self, attr)!r}" for attr in self.__repr_attrs__ if hasattr(self, attr)
        )
        return f"<{self.__class__.__name__}({attrs})>"
