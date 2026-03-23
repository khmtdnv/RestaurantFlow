import logging

from application.dtos.sync import MenuSyncEventDTO
from application.use_cases.menu.sync_menu import SyncMenuUseCase
from infrastructure.database.session import async_session_maker
from presentation.dependencies import get_sync_menu_use_case
from pydantic import ValidationError

log = logging.getLogger(__name__)


async def menu_sync_handler(payload: bytes) -> None:
    try:
        event = MenuSyncEventDTO.model_validate_json(payload)
    except ValidationError as e:
        log.error(f"Invalid AMQP payload: {e}")
        return

    use_case = get_sync_menu_use_case()

    try:
        await use_case.execute(event.menu)
    except Exception:
        log.error("Внутренняя ошибка при синхронизации меню", exc_info=True)
        raise
