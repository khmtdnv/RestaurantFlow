import logging

from application.dto.menu import MenuSyncEvent
from domain.aggregates.item import Item
from domain.interfaces.uow import IUnitOfWork

logger = logging.getLogger("sync_menu")


class SyncMenuUseCase:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, event_data: MenuSyncEvent) -> None:
        async with self.uow:
            items_to_sync = [Item(**item.model_dump()) for item in event_data.menu]
            if items_to_sync:
                await self.uow.item.upsert_many(items_to_sync)
            await self.uow.commit()
