import logging

from application.dto.menu import MenuSyncEvent
from application.use_cases.sync_menu import SyncMenuUseCase
from domain.interfaces.uow import IUnitOfWork
from presentation.api.dependencies import get_uow

logger = logging.getLogger(__name__)


async def handle_menu_sync_event(payload: bytes) -> None:
    event_data = MenuSyncEvent.model_validate_json(payload)

    uow: IUnitOfWork = get_uow()
    use_case = SyncMenuUseCase(uow=uow)

    await use_case.execute(event_data)
