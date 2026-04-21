import json
import logging

from redis.asyncio import Redis
from services.dishes import DishService
from utils.rabbitmq import rabbitmq_publisher
from utils.redis import redis_client
from utils.unitofwork import IUnitOfWork, UnitOfWork

logger = logging.getLogger(__name__)


async def handle_menu_sync_event() -> None:
    redis: Redis = redis_client
    await redis.delete("menu:full")
