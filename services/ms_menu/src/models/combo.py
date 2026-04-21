from typing import TYPE_CHECKING

from db.database import Base, TimestampMixin, id_pk, price
from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.orm import Mapped, relationship

if TYPE_CHECKING:
    from models.dish import Dish

CombosDishes = Table(
    "combos_dishes",
    Base.metadata,
    Column("combo_id", ForeignKey("combos.id", ondelete="CASCADE"), primary_key=True),
    Column("dish_id", ForeignKey("dishes.id", ondelete="CASCADE"), primary_key=True),
)


class Combo(TimestampMixin, Base):
    __tablename__ = "combos"

    id: Mapped[id_pk]
    name: Mapped[str]
    price: Mapped[price]

    # Bidirectional M2M
    dishes: Mapped[list["Dish"]] = relationship(
        secondary="combos_dishes", back_populates="combos", lazy="raise_on_sql"
    )
