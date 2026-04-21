import json
import logging
from typing import Any, Dict

import aio_pika
from application.interfaces.message_broker import IEventPublisher

log = logging.getLogger(__name__)


class RabbitMQPublisher(IEventPublisher):
    def __init__(self, exchange: aio_pika.abc.AbstractExchange):
        self.exchange = exchange

    async def publish(self, routing_key: str, payload: Dict[str, Any]) -> None:
        try:
            body = json.dumps(payload).encode("utf-8")
            message = aio_pika.Message(
                body=body,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            )

            await self.exchange.publish(message=message, routing_key=routing_key)

            log.info(f"Событие '{routing_key}' успешно опубликовано")
        except Exception:
            log.exception(f"Ошибка при отправке события '{routing_key}' в RabbitMQ")
            raise

        return await super().publish(routing_key, payload)
