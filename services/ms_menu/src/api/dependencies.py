from typing import Annotated

from fastapi import Depends
from utils.minio import Minio, get_s3_client
from utils.rabbitmq import RabbitMQPublisher, get_rabbitmq_publisher
from utils.redis import Redis, get_redis
from utils.unitofwork import IUnitOfWork, UnitOfWork

UOWDependency = Annotated[IUnitOfWork, Depends(UnitOfWork)]
BrokerDependency = Annotated[RabbitMQPublisher, Depends(get_rabbitmq_publisher)]
RedisDependency = Annotated[Redis, Depends(get_redis)]
S3Dependency = Annotated[Minio, Depends(get_s3_client)]
