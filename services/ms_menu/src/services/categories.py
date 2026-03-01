from utils.unitofwork import IUnitOfWork


class CategoriesService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def get_categories(self):
        async with self.uow:
            categories = await self.uow.categories.get_all()
            return categories
