import logging
from contextlib import AsyncExitStack, asynccontextmanager

from core.logging import configure_logging
from fastapi import FastAPI
from infrastructure.aiohttp.setup import setup_aiohttp
from infrastructure.rabbitmq.setup import setup_rabbitmq
from infrastructure.redis.setup import setup_redis
from presentation.api.v1.payments import router as payments_router
from presentation.api.v1.webhooks import router as webhooks_router

configure_logging()
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncExitStack() as stack:
        await stack.enter_async_context(setup_aiohttp(app))
        await stack.enter_async_context(setup_redis(app))
        await stack.enter_async_context(setup_rabbitmq(app))

        yield


app = FastAPI(lifespan=lifespan)

app.include_router(payments_router, prefix="/api/v1")
app.include_router(webhooks_router, prefix="/api/v1")
