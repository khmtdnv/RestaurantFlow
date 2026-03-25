import logging
from typing import List

from application.dtos.sync import ItemSyncDTO
from domain.entities.menu_item import MenuItem
from domain.interfaces.uow import IUnitOfWork

log = logging.getLogger(__name__)


class SyncMenuUseCase:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, items_dto: List[ItemSyncDTO]) -> None:
        if not items_dto:
            return

        entities = [
            {
                "id": dto.id,
                "name": dto.name,
                "price": dto.price,
                "is_available": dto.is_available,
            }
            for dto in items_dto
        ]

        async with self.uow:
            await self.uow.menu_repo.upsert_batch(entities)
            await self.uow.commit()

        log.info(f"Синхронизировали {len(entities)} блюдо в меню.")
