import asyncio
import logging
import signal

from config import settings
from infrastructure.message_broker.consumer import RabbitMQConsumer
from presentation.amqp.handlers import handle_menu_sync_event


async def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("worker")

    stop_event = asyncio.Event()

    def handle_shutdown_signal():
        logger.info(
            "Получен сигнал остановки (SIGINT/SIGTERM). Инициируем Graceful Shutdown..."
        )
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, handle_shutdown_signal)
        except NotImplementedError:
            pass

    consumer = RabbitMQConsumer(amqp_url=settings.RABBITMQ_URL)
    await consumer.connect()
    logger.info("Успешное подключение. Начинаем потребление сообщений...")

    try:
        await consumer.consume(
            exchange_name="ms_menu_exchange",
            queue_name="ms_order_sync_queue",
            routing_key="menu.updated",
            handler=handle_menu_sync_event,
            prefetch_count=10,
        )
        await stop_event.wait()

    finally:
        logger.info("Закрываем AMQP соединения и очищаем ресурсы...")
        await consumer.close()
        logger.info("Воркер остановлен штатно.")


if __name__ == "__main__":
    asyncio.run(main())
