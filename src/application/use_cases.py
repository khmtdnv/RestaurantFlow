from src.application.interfaces import UnitOfWork
from src.domain.entities import UserDomain


class RegisterUserUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def execute(self, name: str, phone: str) -> UserDomain:
        async with self.uow:
            existing_user = await self.uow.users.get_by_phone(phone)
            if existing_user:
                raise ValueError("Пользователь с таким номером уже существует")

            # Создаем чистую доменную сущность
            new_user = UserDomain(name=name, phone_number=phone)

            # Сохраняем (репозиторий сам переведет ее в ORM и положит в БД)
            created_user = await self.uow.users.add_one(new_user)
            await self.uow.commit()

            return created_user
