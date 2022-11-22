from __future__ import annotations
import requests
from datetime import date

# from finance.utils import (
from utils import (
    URL_ENDPOINT,
    sleep_safe_blocking,
    get_weekday,
    make_file_paths,
    MARKETS,
    date_logging,
    _file_exists,
    get_today,
)
import os, csv
import asyncmy

from abc import *
from typing import Coroutine, List, ClassVar, Any, Generator
import aiohttp
import json
import csv
from pprint import pprint

# from finance.abstractClass import KRX_data_interface
from abstractClass import KRX_data_interface


class ProgramClass(KRX_data_interface):

    key_used: ClassVar[List[str]] = [
        "ITM_TP_NM",
        "ASK_TRDVOL",
        "BID_TRDVOL",
        "NETBID_TRDVOL",
        "ASK_TRDVAL",
        "BID_TRDVAL",
        "NETBID_TRDVAL",
    ]

    NAME: ClassVar[str] = "program"

    def __init__(self) -> None:
        pass

    def is_empty(self, json_) -> bool:

        if not json_["output"]:
            return True
        return False

    @property
    def csv_path(self) -> os.PathLike:
        """
        return csv file path
        """
        return "./test.csv"

    def save_to_csv(self, csvItems: List[List[Any]]) -> None:
        """
        write or append data~
        """
        # 1. 파일 이미 있는지 확인~
        _exists = _file_exists(self.csv_path)

        _mode = "a" if _exists else "w"

        # 2. 저장 or append 알아서~
        with open(self.csv_path, mode=_mode, encoding="utf-8", newline="") as fp:
            csvwriter = csv.writer(fp)
            if not _exists:
                csvwriter.writerow(["date"] + ProgramClass.key_used)
            # for line_ in csvItems:
            csvwriter.writerows(csvItems)

    def to_csv(self, json_, date_: date) -> None:
        items_ = []
        str_date = date_.strftime("%Y-%m-%d")
        items_raw = json_["output"]

        def parse_to_number(x: str):
            try:
                return int(x.replace(",", ""))
            except ValueError:
                return x

        for item_raw in items_raw:
            [item_raw[key] for key in ProgramClass.key_used]
            item_ = [str_date] + [parse_to_number(item_raw[key]) for key in ProgramClass.key_used]
            items_.append(item_)
        self.save_to_csv(items_)

    def _make_url(self, market: str, at_day: date) -> str:
        program_url = URL_ENDPOINT(for_="program")
        # for market in markets:
        #     for date_ in get_weekday(from_=from_, to_=to_):
        YYYYMMDD = at_day.strftime("%Y%m%d")
        return program_url.build_url(market, start_date=YYYYMMDD, end_date=YYYYMMDD)

    async def get_data(self, market: str, at_day: date):
        # dates_ = get_weekday(from_=from_, to_=to_)

        endpoint = self._make_url(market, at_day=at_day)
        async with aiohttp.ClientSession(headers={"Accept": "application/json"}) as session:
            async with session.post(endpoint) as response:
                if response.status != 200:
                    # TODO : log it
                    return
                # NOTE: 서버측에서 html 형태로 보내서 text으로 처리해야하는 부분이 있음
                html = await response.text()
                try:
                    a = json.loads(html)
                    if self.is_empty(a):
                        print("empty!!")
                        # TODO : log it
                        return
                except Exception as e:
                    # TODO : handle error
                    print("empty!!")
                    print(e)
                    return
        return a["output"]

    def trim_data(self, json_, at_day, market_name) -> List:
        items_ = []

        """     
        "ITM_TP_NM": "차익",
        "ASK_TRDVOL": "742,970",
        "BID_TRDVOL": "1,928,223",
        "NETBID_TRDVOL": "1,185,253",
        "ASK_TRDVAL": "38,055,430,325",
        "BID_TRDVAL": "100,248,070,470",
        "NETBID_TRDVAL": "62,192,640,145"
        """

        keys = {
            "ITM_TP_NM": "PROGRAM_TRADE_TYPE",
            "ASK_TRDVOL": "SELL_VOLUME",
            "BID_TRDVOL": "BUY_VOLUME",
            "NETBID_TRDVOL": "NET_BUY_VOLUME",
            "ASK_TRDVAL": "SELL_VALUE",
            "BID_TRDVAL": "BUY_VALUE",
            "NETBID_TRDVAL": "NET_BUY_VALUE",
        }

        date_ = at_day.strftime("%Y-%m-%d")

        def parse_to_number(x: str):
            try:
                return int(x.replace(",", ""))
            except ValueError:
                return x

        for item_raw in json_:
            # print("=" * 10 + "item_raw" + "=" * 10)
            # pprint(item_raw)
            item_ = [date_, market_name]
            item_ += [parse_to_number(item_raw[k]) for k, v in keys.items()]
            items_.append(item_)
        # print(f"{len(items_)=}")
        return items_

    async def insert_data(self, data_):

        conn = await asyncmy.connect(
            host="127.0.0.1",
            port=3309,
            user="root",
            password="mysql-db",
            db="finance",
            autocommit=True,
        )
        insert_query = """
        INSERT INTO Program_Trade_Data(
            TRADE_DATE,
            MARKET_TYPE_NAME,
            PROGRAM_TRADE_TYPE,
            SELL_VOLUME,
            BUY_VOLUME,
            NET_BUY_VOLUME,
            SELL_VALUE,
            BUY_VALUE,
            NET_BUY_VALUE) VALUES (%s, %s, %s,%s, %s,%s, %s,%s, %s)
        """
        try:
            async with conn.cursor() as curr:
                await curr.executemany(insert_query, data_)
        except Exception as e:
            pprint(data_)
            print(e)
            exit()
        finally:
            conn.close()

    async def run(self):
        pass

    async def run_routine(self) -> None:
        date_ = get_today()
        date_ = date(2022, 11, 22)

        from_ = date(2015, 1, 1)
        # from_ = date(2022, 11, 22)
        to_ = date(2022, 11, 22)
        for dd in get_weekday(from_, to_):
            for market, market_fullname in [(MARKETS.KOSPI, "KOSPI"), (MARKETS.KOSDAQ, "KOSDAQ")]:
                # for market, market_fullname in [
                #     (MARKETS.KOSPI, "KOSPI"),
                # ]:
                print(f"{market} + {dd}")
                raw_data = await self.get_data(market=market, at_day=dd)
                # print(f"{raw_data=}")

                if raw_data is None:
                    await asyncio.sleep(1.2)
                    continue

                data_ = self.trim_data(raw_data, dd, market_fullname)

                await self.insert_data(data_=data_)
                await asyncio.sleep(1.3)


if __name__ == "__main__":
    pass

    import asyncio

    loop = asyncio.get_event_loop()
    pc = ProgramClass()
    loop.run_until_complete(pc.run_routine())
    # loop.run_until_complete(ProgramClass().get_data(["STK"], date(2022, 11, 7), date(2022, 11, 9)))
    # for x in BuyerClass()._make_urls(["krx"], date(2022, 10, 23), date(2022, 10, 28)):
    #     print(x)
