import asyncio

from config import settings
from services.sync_menu import handle_menu_sync_event
from utils.consumer import RabbitMQConsumer


async def main():
    consumer = RabbitMQConsumer(amqp_url=settings.RABBITMQ_URL)
    await consumer.connect()

    try:
        await consumer.consume(
            exchange_name="ms_menu_exchange",
            queue_name="ms_menu_sync_queue",
            routing_key="menu.inner.#",
            handler=handle_menu_sync_event,
            prefetch_count=10,
        )
        # Здесь можно добавить вторую очередь
        await asyncio.Future()

    finally:
        await consumer.close()


if __name__ == "__main__":
    asyncio.run(main())
