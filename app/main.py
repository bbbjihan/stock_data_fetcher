import logging
from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from finance import *

from datetime import timezone, timedelta
from functools import partial

logger = logging.getLogger(__name__)
app = FastAPI()


def build_scheduler() -> AsyncIOScheduler:

    TZ_KST = timezone(timedelta(hours=9), "KST")
    aioScheduler = AsyncIOScheduler(timezone=TZ_KST)

    basicInfo = partial(BasicInfoClass().run, MARKETS.ALL)
    cronTrigger = CronTrigger(minute=1, timezone=TZ_KST)
    ii = IntervalTrigger(seconds=5)
    aioScheduler.add_job(func=basicInfo, trigger=ii)

    def temp():
        print("안녕~~")
        logger.info("안녕!!")

    aioScheduler.add_job(func=temp, trigger=ii)
    # BuyerClass()
    # ProgramClass()
    # SingelSiseClass()
    # StockInfoClass()

    # aioScheduler.add_job()

    return aioScheduler


app.scheduler = build_scheduler()
app.scheduler.start()


@app.get("/")
def hello():
    return "Hello"


# @app.on_event("startup")
# # @repeat_every(seconds=1, logger=logger, wait_first=True)
# def periodic():
#     global counter
#     print("counter is", counter)
#     counter += 1
