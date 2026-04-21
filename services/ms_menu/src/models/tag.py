from db.database import Base, TimestampMixin, id_pk
from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column

DishesTags = Table(
    "dishes_tags",
    Base.metadata,
    Column("dish_id", ForeignKey("dishes.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Tag(TimestampMixin, Base):
    __tablename__ = "tags"

    id: Mapped[id_pk]
    name: Mapped[str] = mapped_column(unique=True)
