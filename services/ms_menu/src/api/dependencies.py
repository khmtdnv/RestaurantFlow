from typing import Annotated

from fastapi import Depends
from utils.minio import Minio, get_s3_client
from utils.rabbitmq import RabbitMQClient, get_rabbitmq_client
from utils.redis import Redis, get_redis
from utils.unitofwork import IUnitOfWork, UnitOfWork

UOWDependency = Annotated[IUnitOfWork, Depends(UnitOfWork)]
BrokerDependency = Annotated[RabbitMQClient, Depends(get_rabbitmq_client)]
RedisDependency = Annotated[Redis, Depends(get_redis)]
S3Dependency = Annotated[Minio, Depends(get_s3_client)]
