from fastapi import APIRouter
from app.api.api_v1.endpoints import stock

api_router = APIRouter()
api_router.include_router(stock.router, prefix="/stock", tags=["stocks"])
