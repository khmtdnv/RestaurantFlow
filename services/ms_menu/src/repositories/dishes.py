from models.dishes import Dishes
from utils.repository import SQLAlchemyRepository


class DishesRepository(SQLAlchemyRepository):
    model = Dishes
