import asyncio
import json
import logging
import uuid

import aio_pika
from config import settings
from models import ProcessedMessage
from redis.asyncio import Redis
from sqlalchemy.dialects.postgresql import insert
from utils.redis import redis_client
from utils.unitofwork import IUnitOfWork, UnitOfWork

logger = logging.getLogger(__name__)


class RetryableEventError(Exception):
    pass


class RejectEventError(Exception):
    pass


async def message_handler(uow: IUnitOfWork, message_id: str, body: str):
    async with uow:
        statement = insert(ProcessedMessage).values(message_id=message_id)
        statement = statement.on_conflict_do_nothing(
            index_elements=["message_id"]
        ).returning(ProcessedMessage.message_id)
        result = await uow.session.execute(statement)
        inserted_id = result.scalar()
        if inserted_id is None:
            return

    redis: Redis = redis_client
    await redis.delete("menu:full")
    logger.info("Кэш по ключу 'menu:full' очищен")


class RabbitMQClient:
    def __init__(self, url: str):
        self.url = url
        self.connection = None
        self.channel = None
        self.retry_header = "x-retry-count"
        self.exchange_name = "menu_events"

    async def connect(self):
        self.connection = await aio_pika.connect_robust(self.url)
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=10)
        self.exchange = await self.channel.declare_exchange(
            self.exchange_name,
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )
        logger.info("Подключение к RabbitMQ успешно создано")

    async def publish(self, routing_key: str, payload: dict, headers: dict):
        payload_json = json.dumps(payload).encode()
        message = aio_pika.Message(
            body=payload_json,
            message_id=str(uuid.uuid4()),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            headers=headers,
        )
        await self.exchange.publish(message, routing_key)  # type: ignore
        logger.info("Сообщение успешно опубликовано")

    async def _handle_retry(self, message: aio_pika.IncomingMessage, routing_key: str):
        if message.headers is None:
            retries: int = 0
        else:
            retries = message.headers.get(self.retry_header, 0)  # type:ignore
            if retries >= 3:
                await message.reject()
                return

        payload = json.loads(message.body)
        headers = {self.retry_header: retries + 1}
        await self.publish(routing_key, payload, headers)
        await message.ack()
        logger.info("Повторная отправка сообщения")

    async def consume(
        self,
        queue_name: str,
        routing_key: str,
        message_handler: callable,  # type:ignore
        stop_event: asyncio.Event,
    ):
        queue = await self.channel.declare_queue(  # type:ignore
            queue_name, durable=True
        )
        await queue.bind(self.exchange, routing_key=routing_key)
        logger.info(
            f"Очередь {queue_name} привязана к {self.exchange_name} с ключом {routing_key}"
        )
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                if stop_event.is_set():
                    logger.info("Сработал stop_event, новые сообщения не принимаем")
                    await message.nack(requeue=True)
                    break

                try:
                    if not message.message_id:
                        logger.warning("Не указан message_id в headers сообщения")
                        raise RejectEventError
                    uow = UnitOfWork()
                    await message_handler(uow, message.message_id, message.body)
                    await message.ack()
                    logger.info("Сообщения успешно обработано")
                except RetryableEventError:
                    logger.warning("Произошла предвиденная ошибка, вызываем ретрай")
                    await self._handle_retry(message, queue_name)  # type:ignore
                except RejectEventError:
                    logger.warning("Произошла ошибка, реджектим сообщение")
                    await message.reject(requeue=False)
                except Exception:
                    logger.warning("Произошла НЕпредвиденная ошибка, вызываем ретрай")
                    await self._handle_retry(message, queue_name)  # type:ignore

    async def close(self):
        if self.channel and not self.channel.is_closed:
            await self.channel.close()
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
        logger.info("Подключение к RabbitMQ успешно закрыто")


_rabbitmqclient = RabbitMQClient(settings.RABBITMQ_URL)


def get_rabbitmq_client() -> RabbitMQClient:
    return _rabbitmqclient
