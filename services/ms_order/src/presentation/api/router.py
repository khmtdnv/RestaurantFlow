from fastapi import APIRouter
from presentation.api.v1.cart import router as cart_router
from presentation.api.v1.order import router as order_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(cart_router)
api_router.include_router(order_router)
