from fastapi import APIRouter
from routers.board import view


def make_router():
    router = APIRouter(prefix="/board", tags=["board stuffs, 게시판"])
    router.include_router(view.router)
    return router


boardRouter = make_router()
