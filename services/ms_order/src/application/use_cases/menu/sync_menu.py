import logging
from typing import List

from application.dtos.sync import ItemSyncDTO
from infrastructure.services.item_synchronizer import ItemSynchronizer
from sqlalchemy.ext.asyncio import async_sessionmaker

logger = logging.getLogger(__name__)


class SyncMenuUseCase:
    def __init__(self, session_factory: async_sessionmaker):
        self._session_factory = session_factory

    async def execute(self, items: List[ItemSyncDTO]) -> None:
        if not items:
            return
        items_data = [item.model_dump() for item in items]

        async with self._session_factory() as session:
            try:
                synchronizer = ItemSynchronizer(session)
                await synchronizer.sync_batch(items_data)
                await session.commit()
                logger.info("ms_order:сообщение обработано")
            except Exception:
                await session.rollback()
                raise
