from typing import TYPE_CHECKING

from models.base import Base, TimestampMixin, price
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from models.categories import Categories


class Dishes(TimestampMixin, Base):
    __tablename__ = "dishes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    price: Mapped[price]
    description: Mapped[str | None] = mapped_column()
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
    )
    category: Mapped["Categories"] = relationship(back_populates="dishes")
