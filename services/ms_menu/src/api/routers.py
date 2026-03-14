from api.categories import category_router
from api.combos import router as combos_router
from api.dishes import menu_router
from api.dishes import router as dishes_router
from api.tags import router as tags_router

all_routers = [
    menu_router,
    category_router,
    dishes_router,
    tags_router,
    combos_router,
]
