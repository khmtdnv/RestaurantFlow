import logging

from application.dtos.sync import MenuSyncEventDTO
from application.use_cases.menu.sync_menu import SyncMenuUseCase
from infrastructure.database.session import async_session_maker
from infrastructure.uow.sqlalchemy_uow import SQLAlchemyUnitOfWork
from pydantic import ValidationError

log = logging.getLogger(__name__)


async def menu_sync_handler(payload: bytes) -> None:
    try:
        event = MenuSyncEventDTO.model_validate_json(payload)
    except ValidationError as e:
        log.error(f"Invalid AMQP payload (Poison Pill): {e}")
        return

    async with async_session_maker() as session:
        uow = SQLAlchemyUnitOfWork(session)
        use_case = SyncMenuUseCase(uow=uow)
        try:
            await use_case.execute(event.menu)
            log.info("Меню успешно синхронизировано.")
        except Exception:
            log.error("Внутренняя ошибка при синхронизации меню", exc_info=True)
            raise
