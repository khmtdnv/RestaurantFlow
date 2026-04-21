from abc import ABC, abstractmethod
from typing import Any, Dict


class IEventPublisher(ABC):
    @abstractmethod
    async def publish(self, routing_key: str, payload: Dict[str, Any]) -> None:
        """Отправляет событие в шину сообщений (RabbitMQ)"""
        pass
