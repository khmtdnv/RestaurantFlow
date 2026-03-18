from infrastructure.database.database import Base, numeric_price
from sqlalchemy.orm import Mapped, mapped_column


class ItemModel(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    name: Mapped[str]
    price: Mapped[numeric_price]
    is_available: Mapped[bool]
