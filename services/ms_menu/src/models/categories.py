from db.db import Base, TimestampMixin
from sqlalchemy.orm import Mapped, mapped_column


class Categories(TimestampMixin, Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[str]
