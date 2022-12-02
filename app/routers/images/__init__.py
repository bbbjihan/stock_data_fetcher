from fastapi import APIRouter
from routers.images import upload


def make_router():
    router = APIRouter(prefix="/image", tags=["image stuffs, 이미지"])
    router.include_router(upload.router)
    return router


imageRouter = make_router()
