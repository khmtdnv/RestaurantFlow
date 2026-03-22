import logging
from typing import Any, Awaitable, Callable

from aio_pika import ExchangeType, connect_robust
from aio_pika.abc import (
    AbstractChannel,
    AbstractIncomingMessage,
    AbstractRobustConnection,
)

logger = logging.getLogger(__name__)

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
        logger.info("Установлено соединение с RabbitMQ и открыт канал.")

    async def close(self) -> None:
        # ! Закрываем канал, затем закрываем соединение
        if self._channel and not self._channel.is_closed:
            await self._channel.close()
            logger.info("AMQP канал закрыт.")

        if self._connection and not self._connection.is_closed:
            await self._connection.close()
            logger.info("AMQP соединение закрыто.")

    async def consume(
        self,
        exchange_name: str,
        queue_name: str,
        routing_key: str,
        handler: MessageHandler,
        prefetch_count: int = 10,
    ) -> str:
        if not self._channel:
            raise RuntimeError("Канал не инициализирован")

        await self._channel.set_qos(prefetch_count=prefetch_count)

        exchange = await self._channel.declare_exchange(
            name=exchange_name, type=ExchangeType.TOPIC, durable=True
        )

        queue = await self._channel.declare_queue(name=queue_name, durable=True)
        await queue.bind(exchange, routing_key=routing_key)

        async def _process_message(message: AbstractIncomingMessage) -> None:
            async with message.process(requeue=True):
                try:
                    await handler(message.body)
                except Exception as e:
                    logger.error(
                        f"Критическая ошибка обработки {message.message_id}: {e}",
                        exc_info=True,
                    )
                    raise

        consumer_tag = await queue.consume(_process_message)
        logger.info(
            f"Консьюмер подписан на очередь {queue_name} с тегом {consumer_tag}"
        )

        return consumer_tag
