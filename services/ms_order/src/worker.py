import asyncio
import logging
import signal

from config import settings
from infrastructure.message_broker.consumer import RabbitMQConsumer
from presentation.amqp.handlers import menu_sync_handler

from .logging import configure_logging


async def main():
    configure_logging()
    log = logging.getLogger(__name__)

    stop_event = asyncio.Event()

    def handle_shutdown_signal():
        log.info("Caught sigint/sigterm. Perfroming shut down.")
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, handle_shutdown_signal)
        except NotImplementedError:
            pass

    consumer = RabbitMQConsumer(amqp_url=settings.RABBITMQ_URL)
    await consumer.connect()
    log.info("Rabbitmq connection established. message consuming started.")

    try:
        await consumer.consume(
            exchange_name="ms_menu_exchange",
            queue_name="ms_order_sync_queue",
            routing_key="menu.updated",
            handler=menu_sync_handler,
            prefetch_count=10,
        )
        await stop_event.wait()

    finally:
        log.info("Closing Rabbimq connection.")
        await consumer.close()
        log.info("Worker successfully stopped.")


if __name__ == "__main__":
    asyncio.run(main())
