import logging

from application.dtos.sync import MenuSyncEventDTO
from application.use_cases.menu.sync_menu import SyncMenuUseCase
from infrastructure.database.session import async_session_maker
from pydantic import ValidationError

log = logging.getLogger(__name__)


async def menu_sync_handler(
    payload: bytes,
) -> None:
    try:
        event = MenuSyncEventDTO.model_validate_json(payload)
    except ValidationError as e:
        log.error(f"Получен невалидный payload. Сообщение дропнуто. Ошибка: {e}")
        return

    items = event.menu
    if not items:
        log.warning("Получен пустой payload для синхронизации меню")
        return

    use_case = SyncMenuUseCase(async_session_maker)
    try:
        await use_case.execute(items)
    except Exception:
        log.error("Внутренняя ошибка при синхронизации меню", exc_info=True)
        raise
