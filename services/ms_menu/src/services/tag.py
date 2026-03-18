from models import Category, Dish, Tag
from models.tag import DishesTags
from schemas.tag import TagCreateIn, TagUpdateIn
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from utils.fake import categories_data, dishes_data, dishes_tags_data, tags_data
from utils.unitofwork import IUnitOfWork


class TagService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def get_tag(self, id: int):
        async with self.uow:
            tag_orm = await self.uow.tag.get_by_id(id)
            if not tag_orm:
                raise ValueError("Тэг не найден")
            return tag_orm

    async def get_tags(self):
        async with self.uow:
            await self._fake()
            tags_orm = await self.uow.tag.get_all()
            return tags_orm

    async def add_tag(self, dto: TagCreateIn):
        async with self.uow:
            tag_orm = Tag(name=dto.name)
            self.uow.tag.add(tag_orm)
            await self.uow.flush()
            return tag_orm

    async def update_tag(self, id: int, dto: TagUpdateIn):
        async with self.uow:
            tag_orm = await self.uow.tag.get_by_id(id)
            if not tag_orm:
                raise ValueError("Тэг не найден")
            dto_dict = dto.model_dump(exclude_unset=True, exclude_none=True)
            self.uow.tag.update(tag_orm, **dto_dict)
            await self.uow.flush()
            return tag_orm

    async def delete_tag(self, id: int):
        async with self.uow:
            tag_orm = await self.uow.tag.get_by_id(id)
            if not tag_orm:
                raise ValueError("Тэг не найден")
            await self.uow.tag.delete(tag_orm)

    async def _fake(self):
        for model, data in [
            (Category, categories_data),
            (Tag, tags_data),
            (Dish, dishes_data),
        ]:
            stmt = pg_insert(model).values(data)
            stmt = stmt.on_conflict_do_nothing(index_elements=["id"])
            await self.uow.session.execute(stmt)

        stmt_tags = pg_insert(DishesTags).values(dishes_tags_data)
        stmt_tags = stmt_tags.on_conflict_do_nothing(
            index_elements=["dish_id", "tag_id"]
        )
        await self.uow.session.execute(stmt_tags)

        tables_to_sync = ["categories", "tags", "dishes"]
        for table_name in tables_to_sync:
            sync_query = text(
                f"""
                SELECT setval(
                    pg_get_serial_sequence('{table_name}', 'id'),
                    COALESCE((SELECT MAX(id) FROM {table_name}), 1)
                );
            """
            )
            await self.uow.session.execute(sync_query)
