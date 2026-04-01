from contextlib import asynccontextmanager

import aio_pika
from core.config import settings
from fastapi import FastAPI


@asynccontextmanager
async def setup_rabbitmq(app: FastAPI):
    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    channel = await connection.channel()
    exchange = await channel.declare_exchange(
        name="ms_payment_exchange",
        type=aio_pika.ExchangeType.TOPIC,
        durable=True,
    )

    app.state.rmq_exchange = exchange

    try:
        yield
    finally:
        await channel.close()
        await connection.close()
