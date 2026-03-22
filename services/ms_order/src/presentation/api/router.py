from fastapi import APIRouter
from presentation.api.v1 import cart

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(cart.router)
