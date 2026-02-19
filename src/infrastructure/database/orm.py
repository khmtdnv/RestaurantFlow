import datetime
from typing import Annotated, Optional

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base

intpk = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[
    datetime.datetime,
    mapped_column(DateTime(timezone=True), server_default=func.now()),
]
updated_at = Annotated[
    datetime.datetime,
    mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    ),
]


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_phone_verified: Mapped[bool] = mapped_column(default=False, nullable=False)
    efresh_token: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


class PhoneVerificationORM(Base):
    __tablename__ = "phone_verifications"

    id: Mapped[intpk]
    phone_number: Mapped[str] = mapped_column(nullable=False)
    code: Mapped[str] = mapped_column(nullable=False)
    is_used: Mapped[bool] = mapped_column(default=False, nullable=False)
    expires_at: Mapped[datetime.datetime] = mapped_column(nullable=False)
    attempts_count: Mapped[int]
