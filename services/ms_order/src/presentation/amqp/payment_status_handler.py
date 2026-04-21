import logging

from application.use_cases.order.update_status import UpdateOrderStatusUseCase
from domain.aggregates.order import OrderStatus
from infrastructure.database.session import async_session_maker
from infrastructure.uow.sqlalchemy_uow import SQLAlchemyUnitOfWork
from pydantic import BaseModel, ValidationError, field_validator

log = logging.getLogger(__name__)


class PaymentEventDTO(BaseModel):
    order_id: str
    status: OrderStatus

    @field_validator("status", mode="before")
    @classmethod
    def map_external_status(cls, raw_status: str) -> OrderStatus:
        mapping = {
            "payment.succeeded": OrderStatus.IN_PROGRESS,
            "payment.waiting_for_capture": OrderStatus.IN_PROGRESS,
            "payment.canceled": OrderStatus.CANCELED,
        }
        return mapping.get(raw_status, OrderStatus.CREATED)


async def payment_status_handler(payload: bytes) -> None:
    try:
        event = PaymentEventDTO.model_validate_json(payload)
    except ValidationError as e:
        log.error(f"Невалидный message.payload: {e}")
        return

    async with async_session_maker() as session:
        uow = SQLAlchemyUnitOfWork(session)
        use_case = UpdateOrderStatusUseCase(uow=uow)
        try:
            await use_case.execute(order_id=event.order_id, new_status=event.status)
            log.info(f"Статус заказа {event.order_id} обновлен на {event.status}.")
        except Exception:
            log.error("Внутренняя ошибка", exc_info=True)
            raise
