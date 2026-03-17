from application.dto.cart import AddItemToCartRequest
from domain.aggregates.cart import Cart, CartItem

# class AddItemToCartUseCase:
#     def __init__(self, uow):
#         self.uow = uow

#     async def execute(self, request: AddItemToCartRequest):

#         price = await self.uow.
# Cart.add_item(dish_id=request.dish_id, quantity=)

#     async def get_menu(self, redis: Redis):

#         cache = await redis.get(self.redis_key)

#         if cache:

#             logger.info("Меню взято из кэша")

#             menu_scheme = MenuOut.model_validate_json(cache)

#             return menu_scheme


#         async with self.uow:

#             dishes = await self.uow.dishes.menu()


#         menu_scheme = MenuOut.model_validate(

#             {"menu": [DishFullOut.model_validate(dish) for dish in dishes]}

#         )


#         menu_dict = menu_scheme.model_dump(mode="json")

#         menu_dict_string = menu_scheme.model_dump_json()


#         await redis.set(self.redis_key, value=menu_dict_string, ex=3600)

#         logger.info("Поместили меню в кэш")


#         await self._publish_event("menu.updated", menu_dict)


#         return menu_scheme


# self.redis_key = "menu:full"
