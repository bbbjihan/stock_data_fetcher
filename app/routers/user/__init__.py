from fastapi import APIRouter
from routers.user import balance
from routers.user import info
from routers.user import stocks
from routers.user import update


def make_router():
    router = APIRouter(prefix="/user", tags=["user stuffs 사용자 관련 정보"])
    router.include_router(info.router)
    return router


userRouter = make_router()
