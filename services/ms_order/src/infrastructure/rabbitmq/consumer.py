import logging
from typing import Awaitable, Callable

from aio_pika import ExchangeType, connect_robust
from aio_pika.abc import (
    AbstractChannel,
    AbstractIncomingMessage,
    AbstractRobustConnection,
)

log = logging.getLogger(__name__)

# ! Контракт для handler, он может принимать только байты и ничего больше
MessageHandler = Callable[[bytes], Awaitable[None]]


class RabbitMQConsumer:
    def __init__(self, amqp_url: str):
        self._amqp_url = amqp_url
        self._connection: AbstractRobustConnection | None = None
        self._channel: AbstractChannel | None = None

    async def connect(self) -> None:
        # ! Устанавливаем соединение и создаем канал
        self._connection = await connect_robust(self._amqp_url)
        self._channel = await self._connection.channel()
        log.info("Connection established, channel created.")

    async def close(self) -> None:
        # ! Закрываем канал, затем закрываем соединение
        if self._channel and not self._channel.is_closed:
            await self._channel.close()
            log.info("Channel closed.")

        if self._connection and not self._connection.is_closed:
            await self._connection.close()
            log.info("Connection closed.")

    async def consume(
        self,
        exchange_name: str,
        queue_name: str,
        routing_key: str,
        handler: MessageHandler,
        prefetch_count: int = 10,
    ) -> str:
        if not self._channel:
            raise RuntimeError("Channel not created.")

        await self._channel.set_qos(prefetch_count=prefetch_count)

        exchange = await self._channel.declare_exchange(
            name=exchange_name, type=ExchangeType.TOPIC, durable=True
        )

        queue = await self._channel.declare_queue(name=queue_name, durable=True)
        await queue.bind(exchange, routing_key=routing_key)

        async def _process_message(message: AbstractIncomingMessage) -> None:
            async with message.process(requeue=False):
                try:
                    await handler(message.body)
                except Exception as e:
                    log.error(
                        f"Message error {message.message_id}: {e}",
                        exc_info=True,
                    )
                    raise

        consumer_tag = await queue.consume(_process_message)
        log.info(f"Consumer binded to {queue_name} with tag {consumer_tag}")

        return consumer_tag
