import base64
import io
import json
import logging
import uuid
from datetime import datetime
from typing import Any

from config import settings
from fastapi import HTTPException, UploadFile
from models import Dish
from redis.asyncio import Redis
from schemas.dishes import DishCreateIn, DishOut, DishUpdateIn
from schemas.menu import DishFullOut, MenuOut
from utils.minio import Minio
from utils.rabbitmq import RabbitMQPublisher
from utils.unitofwork import IUnitOfWork

logger = logging.getLogger(__name__)


class DishService:
    def __init__(self, uow: IUnitOfWork, publisher: RabbitMQPublisher):
        self.uow = uow
        self.publisher = publisher
        self.redis_key = "menu:full"
        self.bucket_name = "menu-images"

    async def _publish_event(self, routing_key: str, payload: dict):
        await self.publisher.publish(
            routing_key=routing_key,
            payload=payload,
        )
        logger.info(f"Создано событие: routing_key = {routing_key}")

    async def upload_image(self, dish_id: int, file: UploadFile, s3: Minio):
        if not file.content_type.startswith("image/"):  # type: ignore
            raise HTTPException(status_code=400, detail="Файл должен быть картинкой")

        file_data = await file.read()
        file_extension = file.filename.split(".")[-1]  # type: ignore
        object_name = f"dish_{id}_{uuid.uuid4().hex}.{file_extension}"

        s3.put_object(
            bucket_name=self.bucket_name,
            object_name=object_name,
            data=io.BytesIO(file_data),
            length=len(file_data),
            content_type=file.content_type,  # type: ignore
        )
        file_url = f"http://{settings.MINIO_URL}/{self.bucket_name}/{object_name}"

        async with self.uow:
            dish = await self.uow.dishes.get_one(id=dish_id)
            if not dish:
                raise ValueError("Блюдо не найдено")

            dish.image_url = file_url

        return file_url

    async def get_dishes(self):
        async with self.uow:
            dishes = await self.uow.dishes.get_dishes()
            return dishes

    async def get_dish(self, id: int):
        async with self.uow:
            dish = await self.uow.dishes.get_by_id(id)
            if not dish:
                raise ValueError("Блюдо не найдено")
            return dish

    async def add_dish(self, dto: DishCreateIn):
        async with self.uow:
            tags_orm = []
            if dto.tag_ids:
                tags_orm = await self.uow.tag.get_tags_by_ids(dto.tag_ids)
                if len(tags_orm) != len(dto.tag_ids):
                    raise ValueError(
                        "Один или несколько указанных тегов не найдены в базе"
                    )
            dish_orm = Dish(
                name=dto.name,
                price=dto.price,
                description=dto.description,
                is_available=dto.is_available,
                category_id=dto.category_id,
                tags=tags_orm,
            )
            logger.warning(dish_orm)
            self.uow.dishes.add(dish_orm)
            await self.uow.session.flush()
            # ORM Object -> model_validate -> pydantic scheme
            # pydantic scheme -> model_dump > python dict
            dish_scheme = DishOut.model_validate(dish_orm)
            dish_dict_for_broker = dish_scheme.model_dump(mode="json")

        await self._publish_event("menu.inner.dish.created", dish_dict_for_broker)

        return dish_scheme

    async def update_dish(self, id: int, dto: DishUpdateIn):
        async with self.uow:
            dish = await self.uow.dishes.get_dish_by_id(id)
            if dish is None:
                raise ValueError("Блюдо не найдено")

            old_price = dish.price
            old_availability = dish.is_available

            if "tag_ids" in dto.model_fields_set:
                if dto.tag_ids:
                    tags = await self.uow.tag.get_tags_by_ids(dto.tag_ids)
                    if len(tags) != len(dto.tag_ids):
                        raise ValueError(
                            "Один или несколько указанных тегов не найдены в базе"
                        )
                    dish.tags = tags
                else:
                    dish.tags = []

            dto_dict = dto.model_dump(exclude_unset=True, exclude={"tag_ids"})
            if dto_dict:
                self.uow.dishes.update(dish, **dto_dict)

            await self.uow.session.flush()

            dish_scheme = DishOut.model_validate(dish)
            dish_dict_for_broker = dish_scheme.model_dump(mode="json")

        if old_price != dish_scheme.price:
            await self._publish_event("menu.inner.price.change", dish_dict_for_broker)

        if old_availability != dish_scheme.is_available:
            await self._publish_event(
                "menu.inner.item.availability", dish_dict_for_broker
            )

        return dish_scheme

    async def delete_dish(self, id: int):
        async with self.uow:
            dish_orm = await self.uow.dishes.get_by_id(id)

            if not dish_orm:
                raise ValueError("Блюдо не найдено")

            await self.uow.dishes.delete(dish_orm)
            await self.uow.session.flush()

            dish_scheme = DishOut.model_validate(dish_orm)
            dish_dict = dish_scheme.model_dump(mode="json")

        await self._publish_event("menu.inner.dish.deleted", dish_dict)

        return dish_scheme

    async def get_menu(self, redis: Redis):
        cache = await redis.get(self.redis_key)
        if cache:
            logger.info("Меню взято из кэша")
            menu_scheme = MenuOut.model_validate_json(cache)
            return menu_scheme

        async with self.uow:
            dishes = await self.uow.dishes.menu()

        menu_scheme = MenuOut.model_validate(
            {"menu": [DishFullOut.model_validate(dish) for dish in dishes]}
        )

        menu_dict = menu_scheme.model_dump(mode="json")
        menu_dict_string = menu_scheme.model_dump_json()

        await redis.set(self.redis_key, value=menu_dict_string, ex=3600)
        logger.info("Поместили меню в кэш")

        await self._publish_event("menu.updated", menu_dict)

        return menu_scheme

    async def get_menu_offset(self, offset: int, limit: int):
        async with self.uow:
            dishes = await self.uow.dishes.menu_offset(offset, limit)
            total = await self.uow.dishes.menu_offset_count()
            if not total:
                total = 0

        menu_scheme = MenuOut.model_validate(
            {"menu": [DishFullOut.model_validate(dish) for dish in dishes]}
        )

        return {
            "data": menu_scheme,
            "limit": limit,
            "offset": offset,
            "total": total,
            "returned_count": len(dishes),
            "has_next": offset + limit < total,
            "has_prev": offset > 0,
            "next_offset": offset + limit if offset + limit < total else None,
            "prev_offset": max(0, offset - limit) if offset > 0 else None,
        }

    async def get_menu_page(self, page: int, per_page: int):
        offset = (page - 1) * per_page

        async with self.uow:
            dishes = await self.uow.dishes.menu_offset(offset, per_page)
            total = await self.uow.dishes.menu_offset_count()

        if not total:
            total = 0

        total_pages = (total + per_page - 1) // per_page

        menu_scheme = MenuOut.model_validate(
            {"menu": [DishFullOut.model_validate(dish) for dish in dishes]}
        )

        return {
            "data": menu_scheme,
            "current_page": page,
            "per_page": per_page,
            "total_items": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        }

    def _encode_cursor(self, data: dict[str, Any]) -> str:
        """Кодируем данные в безопасный base64 курсор"""
        json_str = json.dumps(data, default=str)
        return base64.b64encode(json_str.encode()).decode()

    def _decode_cursor(self, cursor: str) -> dict[str, Any]:
        """Декодируем курсор обратно в данные"""
        try:
            json_str = base64.b64decode(cursor.encode()).decode()
            return json.loads(json_str)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid cursor format")

    async def get_menu_cursor(self, cursor: str | None, size: int):
        last_id = 0

        if cursor:
            cursor_data = self._decode_cursor(cursor)
            last_id = cursor_data["last_id"]

        async with self.uow:
            dishes = await self.uow.dishes.menu_cursor(last_id, size)

        next_cursor = None
        if dishes:
            next_cursor = self._encode_cursor(
                {"last_id": dishes[-1].id, "timestamp": datetime.now().isoformat()}
            )

        menu_scheme = MenuOut.model_validate(
            {"menu": [DishFullOut.model_validate(dish) for dish in dishes]}
        )

        return {
            "data": menu_scheme,
            "next_cursor": next_cursor,
            "size": size,
        }
