import logging

from application.dto.sync import MenuSyncEventDTO
from application.use_cases.menu_sync import SyncMenuUseCase
from infrastructure.database.database import async_session_factory
from pydantic import ValidationError

logger = logging.getLogger(__name__)


async def handle_menu_sync_event(
    payload: bytes,
) -> None:
    try:
        event = MenuSyncEventDTO.model_validate_json(payload)
    except ValidationError as e:
        logger.error(f"Получен невалидный payload. Сообщение дропнуто. Ошибка: {e}")
        return

    items = event.menu
    if not items:
        logger.warning("Получен пустой payload для синхронизации меню")
        return

    use_case = SyncMenuUseCase(async_session_factory)
    try:
        await use_case.execute(items)
    except Exception:
        logger.error("Внутренняя ошибка при синхронизации меню", exc_info=True)
        raise
