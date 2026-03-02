from api.categories import router as categories_router
from api.dishes import router as dishes_router

all_routers = [
    categories_router,
    dishes_router,
]
