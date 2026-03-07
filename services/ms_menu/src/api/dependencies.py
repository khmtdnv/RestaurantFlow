from typing import Annotated

from fastapi import Depends
from utils.rabbitmq import RabbitMQClient, rabbitmq_client
from utils.redis import Redis, get_redis
from utils.unitofwork import IUnitOfWork, UnitOfWork


def get_rabbitmq_client() -> RabbitMQClient:
    return rabbitmq_client


UOWDependency = Annotated[IUnitOfWork, Depends(UnitOfWork)]
BrokerDependency = Annotated[RabbitMQClient, Depends(get_rabbitmq_client)]
RedisDependency = Annotated[Redis, Depends(get_redis)]
