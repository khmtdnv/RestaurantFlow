from typing import TYPE_CHECKING

from db.database import Base, TimestampMixin, id_pk, price
from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from models.category import Category
    from models.combo import Combo
    from models.tag import Tag


class Dish(TimestampMixin, Base):
    __tablename__ = "dishes"

    id: Mapped[id_pk]
    name: Mapped[str]
    price: Mapped[price]
    description: Mapped[str | None]
    is_available: Mapped[bool] = mapped_column(server_default=text("true"))
    image_url: Mapped[str | None]

    # M2O
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
    )
    category: Mapped["Category | None"] = relationship(back_populates="dishes", lazy="raise_on_sql")

    # Unidirectional M2M
    tags: Mapped[list["Tag"]] = relationship(secondary="dishes_tags", lazy="raise_on_sql")

    # Bidirectional M2M
    combos: Mapped[list["Combo"]] = relationship(
        secondary="combos_dishes", back_populates="dishes", lazy="raise_on_sql"
    )
