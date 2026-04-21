from models import Combo
from schemas.combo import ComboCreateIn, ComboOut, ComboUpdateIn
from utils.unitofwork import IUnitOfWork


class ComboService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def get_combo(self, id: int):
        async with self.uow:
            combo: Combo | None = await self.uow.combo.get_combo_by_id(id)
            if not combo:
                raise ValueError("Комбо не найдено")

            combo_scheme = ComboOut.model_validate(combo)

            return combo_scheme

    async def get_combos(self):
        async with self.uow:
            combos = await self.uow.combo.get_combos()

            combo_scheme: list[ComboOut] = []
            for combo in combos:
                combo_scheme.append(ComboOut.model_validate(combo))

            return combo_scheme

    async def add_combo(self, dto: ComboCreateIn):
        async with self.uow:
            dishes = []

            if dto.dishes_ids:
                dishes = await self.uow.dishes.get_objects(dto.dishes_ids)
                if len(dishes) != len(dto.dishes_ids):
                    raise ValueError("Один или несколько указанных блюд не найдены в базе")

            combo = Combo(name=dto.name, price=dto.price, dishes=dishes)
            self.uow.combo.add(combo)

            await self.uow.flush()
            combo_scheme = ComboOut.model_validate(combo)

            return combo_scheme

    async def update_combo(self, id: int, dto: ComboUpdateIn):
        async with self.uow:
            combo = await self.uow.combo.get_combo_by_id(id)
            if not combo:
                raise ValueError("Комбо не найдено")

            if "dishes_ids" in dto.model_fields_set:
                if dto.dishes_ids:
                    dishes = await self.uow.dishes.get_objects(dto.dishes_ids)
                    if len(dishes) != len(dto.dishes_ids):
                        raise ValueError("Один или несколько указанных блюд не найдены в базе")
                    combo.dishes = dishes
                else:
                    combo.dishes = []

            dto_dict = dto.model_dump(exclude_unset=True, exclude={"dishes_ids"})
            if dto_dict:
                self.uow.combo.update(combo, **dto_dict)

            await self.uow.flush()
            combo_scheme = ComboOut.model_validate(combo)

            return combo_scheme

    async def delete_combo(self, id: int):
        async with self.uow:
            combo = await self.uow.combo.get_combo_by_id(id)
            if not combo:
                raise ValueError("Комбо не найдено")
            await self.uow.combo.delete(combo)
