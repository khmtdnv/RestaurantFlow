from typing import TYPE_CHECKING, List

from db.database import Base, TimestampMixin, id_pk
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from models.dish import Dish


class Category(TimestampMixin, Base):
    __tablename__ = "categories"

    id: Mapped[id_pk]
    name: Mapped[str] = mapped_column()

    # ONE TO MANY
    dishes: Mapped[List["Dish"]] = relationship(back_populates="category", lazy="raise_on_sql")
