import logging
from dataclasses import dataclass

from application.interfaces.message_broker import IEventPublisher
from domain.interfaces.transaction_repository import ITransactionRepository

log = logging.getLogger(__name__)


@dataclass
class WebhookDTO:
    event: str
    payment_id: str
    order_id: str | None


class ProcessWebhookUseCase:
    def __init__(self, publisher: IEventPublisher):
        self.publisher = publisher

    async def execute(self, dto: WebhookDTO) -> None:
        log.info(f"Начата обработка вебхука: {dto.event} для платежа {dto.payment_id}")

        if dto.event == "payment.succeeded":
            if not dto.order_id:
                log.error(f"Платеж {dto.payment_id} успешен, но order_id отсутствует в metadata!")
                return

            await self.publisher.publish(
                routing_key="payment.succeeded",
                payload={"order_id": dto.order_id, "status": dto.event},
            )
            log.info(f"Событие payment.succeeded опубликовано для заказа {dto.order_id}")

        elif dto.event == "payment.canceled":
            if dto.order_id:
                await self.publisher.publish(
                    routing_key="payment.canceled",
                    payload={"order_id": dto.order_id, "status": dto.event},
                )

        elif dto.event == "payment.waiting_for_capture":
            if dto.order_id:
                await self.publisher.publish(
                    routing_key="payment.waiting_for_capture",
                    payload={"order_id": dto.order_id, "status": dto.event},
                )
