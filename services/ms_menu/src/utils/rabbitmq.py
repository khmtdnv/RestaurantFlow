import asyncio
import json
import logging

from aio_pika import DeliveryMode, ExchangeType, Message, connect_robust
from aio_pika.abc import AbstractChannel, AbstractExchange, AbstractRobustConnection

logger = logging.getLogger(__name__)


class RabbitMQPublisher:
    def __init__(self):
        self._connection: AbstractRobustConnection | None = None
        self._channel: AbstractChannel | None = None
        self._exchange: AbstractExchange | None = None

    async def connect_and_init(self, amqp_url: str, exchange_name: str):
        # ? Метод вызывается строго один раз при старте приложения

        logger.info(f"Connecting to RabbitMQ at {amqp_url}...")
        self._connection = await connect_robust(url=amqp_url, timeout=5.0)
        self._channel = await self._connection.channel()
        self._exchange = await self._channel.declare_exchange(
            name=exchange_name,
            type=ExchangeType.TOPIC,
            durable=True,  # -> exchange переживает рестарт брокера
        )

    async def close(self):
        # ? Метод вызывается строго один раз при остновке приложения.
        if self._connection and not self._connection.is_closed:
            await self._connection.close()

    async def publish(self, routing_key: str, payload: dict):
        if not self._exchange:
            raise RuntimeError("Сначала нужно вызвать connect_and_init")

        message = Message(
            body=json.dumps(payload).encode(),
            delivery_mode=DeliveryMode.PERSISTENT,
        )
        await self._exchange.publish(message, routing_key=routing_key)
        logger.info(f"ms_menu:сообщение опубликовано {routing_key}")


rabbitmq_publisher = RabbitMQPublisher()


def get_rabbitmq_publisher() -> RabbitMQPublisher:
    return rabbitmq_publisher
