from domain.interfaces.uow import IUnitOfWork
from infrastructure.repositories.order_repository import SqlAlchemyOrderRepository
from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyUnitOfWork(IUnitOfWork):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.dishes = SqlAlchemyOrderRepository(self.session)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
