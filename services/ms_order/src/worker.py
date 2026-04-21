import asyncio
import logging
import signal

from core.config import settings
from core.logging import configure_logging
from infrastructure.rabbitmq.consumer import RabbitMQConsumer
from presentation.amqp.menu_sync_handler import menu_sync_handler
from presentation.amqp.payment_status_handler import payment_status_handler
from tenacity import before_sleep_log, retry, stop_after_attempt, wait_exponential

configure_logging()
log = logging.getLogger(__name__)


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
    before_sleep=before_sleep_log(log, logging.WARNING),
)
async def connect_with_retry(consumer: RabbitMQConsumer):
    await consumer.connect()


async def main():
    event = asyncio.Event()

    def handle_shutdown_signal():
        log.info("Остановка RabbitMQ")
        event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, handle_shutdown_signal)
        except NotImplementedError:
            pass

    consumer = RabbitMQConsumer(amqp_url=settings.RABBITMQ_URL)
    await connect_with_retry(consumer)
    log.info("RabbitMQ готов")

    try:
        await consumer.consume(
            exchange_name="ms_menu_exchange",
            queue_name="ms_order_sync_queue",
            routing_key="menu.updated",
            handler=menu_sync_handler,
            prefetch_count=10,
        )
        await consumer.consume(
            exchange_name="ms_payment_exchange",
            queue_name="ms_order_payment_queue",
            routing_key="payment.succeeded",
            handler=payment_status_handler,
            prefetch_count=10,
        )
        await event.wait()
    finally:
        await consumer.close()


if __name__ == "__main__":
    asyncio.run(main())
