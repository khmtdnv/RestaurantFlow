import asyncio
import logging

from application.handlers.sync_menu import handle_menu_sync_event
from config import settings
from infrastructure.message_broker.consumer import RabbitMQConsumer


async def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("worker")

    consumer = RabbitMQConsumer(amqp_url=settings.RABBITMQ_URL)
    await consumer.connect()
    logger.info("хаваем")
    try:
        await consumer.consume(
            exchange_name="ms_menu_exchange",
            queue_name="ms_order_menu_sync_queue",
            routing_key="menu.updated",
            handler=handle_menu_sync_event,
            prefetch_count=10,
        )
        # Здесь можно добавить вторую очередь
        await asyncio.Future()

    finally:
        await consumer.close()


if __name__ == "__main__":
    asyncio.run(main())
