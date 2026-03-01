from typing import TYPE_CHECKING, List

from models.base import Base, TimestampMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from models.dishes import Dishes


class Categories(TimestampMixin, Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    dishes: Mapped[List["Dishes"]] = relationship(
        back_populates="category",
        cascade="all, delete-orphan",
    )
