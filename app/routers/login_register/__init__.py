from fastapi import APIRouter
from routers.login_register import login
from routers.login_register import register


def make_router():
    router = APIRouter(prefix="/auth", tags=["Login and Register"])
    router.include_router(login.router)
    router.include_router(register.router)
    return router


loginRegisterRouter = make_router()
