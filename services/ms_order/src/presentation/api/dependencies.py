from typing import Annotated

from domain.interfaces.uow import IUnitOfWork
from fastapi import Depends
from infrastructure.uow.sqlalchemy_uow import SqlAlchemyUnitOfWork

UOWDependency = Annotated[IUnitOfWork, Depends(SqlAlchemyUnitOfWork)]
