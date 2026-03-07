import asyncio
import json
import logging

import aio_pika
from config import settings
from redis.asyncio import Redis
from utils.redis import redis_client


class RabbitMQClient:
    def __init__(self, redis: Redis):
        self.connection = None
        self.channel = None
        self.exchange = None
        self.redis = redis
        self.exchange_name = "menu_events"

    async def connect(self):
        self.connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
        self.channel = await self.connection.channel()

        self.exchange = await self.channel.declare_exchange(
            self.exchange_name, aio_pika.ExchangeType.TOPIC, durable=True
        )

    async def disconnect(self):
        if self.channel:
            await self.channel.close()
        if self.connection:
            await self.connection.close()

    async def publish(self, routing_key: str, payload: dict):
        payload_json = json.dumps(payload).encode()
        message = aio_pika.Message(
            payload_json,
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )
        await self.exchange.publish(message, routing_key)  # type: ignore

    async def consume(self, queue_name: str, routing_key: str):
        queue = await self.channel.declare_queue(queue_name, durable=True)  # type: ignore

        await queue.bind(self.exchange, routing_key=routing_key)  # type: ignore

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                try:
                    logging.info(
                        f"Получено событие: {message.routing_key}. Очищаем кеш."
                    )
                    await self.redis.delete("menu:full")

                    await message.ack()
                    logging.info("Кеш меню успешно очищен")

                except Exception as e:
                    logging.error(f"Ошибка работы с Redis: {e}.")
                    await message.nack(requeue=True)
                    await asyncio.sleep(5)


rabbitmq_client = RabbitMQClient(redis_client)
