from src.application.interfaces import AbstractUnitOfWork
from src.database import async_session_factory
from src.infrastructure.repositories import PhoneVerificationRepository, UserRepository


class SQLAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.session_factory = async_session_factory

    async def __aenter__(self):
        self.session = self.session_factory()

        self.users = UserRepository(self.session)
        self.verifications = PhoneVerificationRepository(self.session)

        return self

    async def __aexit__(self, *args):
        await self.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
