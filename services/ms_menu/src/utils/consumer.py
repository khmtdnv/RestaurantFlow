import asyncio
import json
import logging
from typing import Awaitable, Callable

from aio_pika import ExchangeType, IncomingMessage, connect_robust
from aio_pika.abc import AbstractIncomingMessage, AbstractRobustConnection

logger = logging.getLogger(__name__)


class RabbitMQConsumer:
    def __init__(self, amqp_url: str):
        self._amqp_url = amqp_url
        self._connection: AbstractRobustConnection | None = None

    async def connect(self):
        self._connection = await connect_robust(self._amqp_url)

    async def close(self):
        if self._connection and not self._connection.is_closed:
            await self._connection.close()

    async def consume(
        self,
        exchange_name: str,
        queue_name: str,
        routing_key: str,
        handler: Callable,
        prefetch_count: int = 10,
    ):
        if not self._connection:
            raise RuntimeError("Консьюмер не подключен к Rabbitmq")

        channel = await self._connection.channel()
        await channel.set_qos(prefetch_count=prefetch_count)

        exchange = await channel.declare_exchange(
            name=exchange_name, type=ExchangeType.TOPIC, durable=True
        )

        queue = await channel.declare_queue(name=queue_name, durable=True)
        await queue.bind(exchange, routing_key=routing_key)

        async def _process_message(message: AbstractIncomingMessage):
            async with message.process(requeue=False):
                try:
                    logger.info("Прошли в _process_message")
                    await handler()
                except Exception as e:
                    logger.error(
                        f"Не удалось обработать сообщение {message.message_id}: {e}"
                    )
                    raise

        await queue.consume(_process_message)
