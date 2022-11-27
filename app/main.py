import logging
from fastapi import FastAPI, WebSocket, middleware
from fastapi_utils.tasks import repeat_every
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from datetime import timezone, timedelta
from functools import partial
from routers.stock import by_name, by_stat
from routers.stock import general
from routers.user import login, register, update
from middlewares.token_validator import access_control

logger = logging.getLogger(__name__)


def build_app():
    app = FastAPI()
    app.include_router(by_name.router)
    app.include_router(by_stat.router)
    app.include_router(general.router)
    app.include_router(login.router)
    app.include_router(register.router)
    app.include_router(update.router)

    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.middleware.cors import CORSMiddleware

    app.add_middleware(middleware_class=BaseHTTPMiddleware, dispatch=access_control)
    return app


app = build_app()


@app.get("/test")
async def test():
    return 200


# @app.websocket("/ws")
# async def websocket_temp(websocket: WebSocket):
#     await websocket.accept()
#     while True:
#         data = await websocket.receive_text()
#         await websocket.send_text(f"Message text was: {data}")


"""
def build_scheduler() -> AsyncIOScheduler:

    TZ_KST = timezone(timedelta(hours=9), "KST")
    aioScheduler = AsyncIOScheduler(timezone=TZ_KST)

    basicInfo = partial(BasicInfoClass().run, MARKETS.ALL)
    cronTrigger = CronTrigger(minute=1, timezone=TZ_KST)
    ii = IntervalTrigger(seconds=5)
    # aioScheduler.add_job(func=basicInfo, trigger=ii)
    # aioScheduler.add_job(func=basicInfo, trigger=ii)
    # aioScheduler.add_job(func=basicInfo, trigger=ii)
    # aioScheduler.add_job(func=basicInfo, trigger=ii)

    def temp():
        print("안녕~~")
        logger.info("안녕!!")

    aioScheduler.add_job(func=temp, trigger=ii)
    # BuyerClass()
    # ProgramClass()
    singelSise = SingelSiseClass()
    # aioScheduler.add_job(func=partial(singelSise.run, ["KR7005930003"]), trigger=ii)
    # StockInfoClass()

    # aioScheduler.add_job()

    return aioScheduler


app.scheduler = build_scheduler()
app.scheduler.start()
"""


@app.on_event("startup")
async def startup():
    from database.setup import setup

    await setup()

    print("finished setup")


@app.on_event("shutdown")
async def startup():
    pass


@app.get("/")
def hello():
    return "Hello"
