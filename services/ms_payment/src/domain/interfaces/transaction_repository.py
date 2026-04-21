from abc import ABC, abstractmethod


class ITransactionRepository(ABC):
    @abstractmethod
    async def update_status(self, payment_id: str, new_status: str) -> None:
        """Обновляет статус транзакции в БД по её ID от ЮКассы"""
        pass
