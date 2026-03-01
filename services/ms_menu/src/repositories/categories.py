from models.categories import Categories
from utils.repository import SQLAlchemyRepository


class CategoriesRepository(SQLAlchemyRepository):
    model = Categories
