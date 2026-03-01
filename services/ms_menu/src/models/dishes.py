from db.db import Base, TimestampMixin
from sqlalchemy.orm import Mapped, mapped_column


class Dishes(TimestampMixin, Base):
    __tablename__ = "dishes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    price: Mapped[int]
    description: Mapped[str]
