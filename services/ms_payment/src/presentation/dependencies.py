import os

import aio_pika
import aiohttp
from application.interfaces.message_broker import IEventPublisher
from application.usecases.create_payment import CreatePaymentUseCase
from application.usecases.process_webhook import ProcessWebhookUseCase
from core.config import settings
from domain.interfaces.payment_gateway import IPaymentGateway
from fastapi import Depends, Request
from infrastructure.rabbitmq.publisher import RabbitMQPublisher
from infrastructure.yookassa.client import YookassaClient
from infrastructure.yookassa.gateway import YookassaGatewayAdapter
from redis.asyncio import Redis


async def get_rabbitmq_exchange(request: Request) -> aio_pika.abc.AbstractExchange:
    return request.app.state.rmq_exchange


async def get_rabbitmq_publisher(
    exchange: aio_pika.abc.AbstractExchange = Depends(get_rabbitmq_exchange),
) -> IEventPublisher:
    return RabbitMQPublisher(exchange=exchange)


async def get_process_webhook_use_case(
    publisher: IEventPublisher = Depends(get_rabbitmq_publisher),
) -> ProcessWebhookUseCase:
    return ProcessWebhookUseCase(publisher=publisher)


async def get_redis_client(request: Request) -> Redis:
    return request.app.state.redis_client


async def get_aiohttp_session(request: Request) -> aiohttp.ClientSession:
    return request.app.state.http_session


async def get_yookassa_client(
    session: aiohttp.ClientSession = Depends(get_aiohttp_session),
) -> YookassaClient:

    return YookassaClient(
        http_client=session,
        base_url="https://api.yookassa.ru/v3/payments",
        shop_id=settings.YOOKASSA_SHOP_ID,
        secret_key=settings.YOOKASSA_SECRET_KEY,
    )


async def get_payment_gateway(
    client: YookassaClient = Depends(get_yookassa_client),
) -> IPaymentGateway:
    return YookassaGatewayAdapter(client=client)


async def get_create_payment_use_case(
    gateway: IPaymentGateway = Depends(get_payment_gateway),
) -> CreatePaymentUseCase:
    return CreatePaymentUseCase(gateway=gateway)
