from domain.aggregates.order import OrderStatus
from infrastructure.database.core import Base, numeric_price
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class OrderItemModel(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    dish_id: Mapped[int] = mapped_column()
    quantity: Mapped[int] = mapped_column()
    price: Mapped[numeric_price] = mapped_column()


class OrderModel(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[OrderStatus] = mapped_column(String(50))
    price: Mapped[numeric_price] = mapped_column()

    items: Mapped[list[OrderItemModel]] = relationship(
        lazy="selectin", cascade="all, delete-orphan"
    )
