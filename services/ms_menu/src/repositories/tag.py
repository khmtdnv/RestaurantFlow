from models import Tag
from sqlalchemy import select
from utils.repository import SQLAlchemyRepository


class TagRepository(SQLAlchemyRepository):
    model = Tag

    async def get_tags_by_ids(self, tag_ids: list[int]):
        statement = select(self.model).where(self.model.id.in_(tag_ids))
        result = await self.session.execute(statement)
        result = list(result.scalars().all())
        return result
