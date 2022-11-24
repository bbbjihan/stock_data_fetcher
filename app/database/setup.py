"""
mysql 커넥터 만들어서 DB에 저장하게 만드는거
"""


DATABASE_URL = "mysql+asyncmy://root:mysql-db@127.0.0.1:3309?charset=utf8mb4"

import asyncio
import asyncmy
from asyncmy.pool import Pool
from asyncmy.cursors import DictCursor
from itertools import chain

# from database.settings import CREATE_TABLE


async def create_database():
    conn = await asyncmy.connect(host="127.0.0.1", port=3309, user="root", password="mysql-db")

    async with conn.cursor() as curr:
        await curr.execute("SHOW DATABASES;")
        r = await curr.fetchall()
        if "finance" not in chain(*r):
            print("database <finance> does not exists")
            await curr.execute("CREATE DATABASE finance")


class CREATE_TABLE:
    live_price = """
    CREATE TABLE IF NOT EXISTS `finance`.`LivePrice` (
    `ISU_CD` INT NOT NULL,
    `market_time` DATETIME NOT NULL,
    `price` INT UNSIGNED NOT NULL,
    PRIMARY KEY (`ISU_CD`))
    ENGINE = InnoDB
    DEFAULT CHARACTER SET = utf8;
    """

    KOSPI_DAY_SUMMARY = """
    CREATE TABLE IF NOT EXISTS `finance`.`KOSPI_day_summary` (
    `date` DATE NOT NULL,
    `ISU_CD` VARCHAR(45) NOT NULL,
    # `ISU_CD_KR` VARCHAR(45) NOT NULL,
    `CLOSE_PRICE` INT NOT UNSIGNED NULL,
    `OPEN_PRICE` INT NOT UNSIGNED NULL,
    `HIGH_PRICE` INT NOT UNSIGNED NULL,
    `LOW_PRICE` INT NOT UNSIGNED NULL,
    `CMPR_PREV_PRICE` INT NOT NULL,
    `CMPR_PREV_RATE` FLOAT(2,2) NOT NULL,
    `TRADE_VOLUME` BIGINT UNSIGNED NOT NULL,
    `TRADE_VALUE` BIGINT UNSIGNED NOT NULL,
    `MARKET_CAP` BIGINT UNSIGNED NOT NULL,
    `LIST_SHARES` BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (`ISU_CD`, `date`));
    """

    STOCK_STATE = """
    CREATE TABLE IF NOT EXISTS `finance`.`stock_state` (
    `stockStateCode` INT NOT NULL,
    `message` VARCHAR(255) NOT NULL,
    PRIMARY KEY (`stockStateCode`));
    """

    STOCK_INFO = """
    CREATE TABLE IF NOT EXISTS `finance`.`Stock_Info` (
    `ISU_CODE` INT NOT NULL,
    `ISU_CODE_KR` VARCHAR(45) NULL,
    `ISU_ABBRV` VARCHAR(45) NULL,
    `ISU_NAME` VARCHAR(45) NULL,
    `ISU_NAME_EN` VARCHAR(45) NULL,
    `NAME_KR` VARCHAR(45) NULL,
    `summary` VARCHAR(255) NULL,
    `STATE_CODE` INT NULL,
    `MARKET_NAME` VARCHAR(45) NULL,
    `MARKET_ID` VARCHAR(45) NULL,
    PRIMARY KEY (`ISU_CODE`));
    """


async def create_tables():
    conn = await asyncmy.connect(
        host="127.0.0.1",
        port=3309,
        user="root",
        password="mysql-db",
        db="finance",
        autocommit=True,
    )

    async with conn.cursor() as curr:
        await curr.execute(CREATE_TABLE.live_price)
        await curr.execute(CREATE_TABLE.KOSPI_DAY_SUMMARY)
        await curr.execute(CREATE_TABLE.live_price)
        await curr.execute(CREATE_TABLE.live_price)
        await curr.execute(CREATE_TABLE.live_price)
        await curr.execute(CREATE_TABLE.live_price)


async def setup():
    await create_database()
    # await create_tables()
    pass


if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(setup())
    # loop.run_until_complete(execute("select 10"))
