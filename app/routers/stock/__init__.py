from fastapi import APIRouter
from routers.stock import search
from routers.stock import today
from routers.stock import live_data
from routers.stock import info


def make_router():
    router = APIRouter(prefix="/stock", tags=["stock 주식 정보"])
    router.include_router(search.router)
    router.include_router(info.router)
    return router


stockRouter = make_router()
