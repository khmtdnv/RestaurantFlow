import datetime
from decimal import Decimal
from typing import Annotated

from sqlalchemy import DateTime, MetaData, Numeric, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

created_at = Annotated[
    datetime.datetime,
    mapped_column(DateTime(timezone=False), server_default=func.now()),
]
updated_at = Annotated[
    datetime.datetime,
    mapped_column(DateTime(timezone=False), onupdate=func.now(), nullable=True),
]

price = Annotated[
    Decimal,
    mapped_column(Numeric(10, 2), nullable=False),
]


class TimestampMixin:
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


metadata_obj = MetaData(schema="menu")


class Base(DeclarativeBase):
    repr_cols_num = 3
    repr_cols = tuple()

    def __repr__(self):
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")
        return f"<{self.__class__.__name__} {','.join(cols)}>"
