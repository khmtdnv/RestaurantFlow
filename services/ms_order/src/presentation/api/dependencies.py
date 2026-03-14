from typing import Annotated

from domain.interfaces.uow import IUnitOfWork
from fastapi import Depends
from infrastructure.database.database import async_session_factory
from infrastructure.uow.sqlalchemy_uow import SqlAlchemyUnitOfWork


def get_uow() -> IUnitOfWork:
    return SqlAlchemyUnitOfWork(session_factory=async_session_factory)


UOWDependency = Annotated[IUnitOfWork, Depends(SqlAlchemyUnitOfWork)]
