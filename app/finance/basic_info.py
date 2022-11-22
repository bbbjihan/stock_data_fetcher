from __future__ import annotations
import requests
from datetime import date, datetime, timezone, timedelta

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
import json
from pprint import pprint
from abc import *
from typing import Coroutine, List, ClassVar, Any, Generator
import aiohttp
import asyncio
import asyncmy

# from finance.abstractClass import KRX_data_interface
from abstractClass import KRX_data_interface


class BasicInfoClass(KRX_data_interface):

    key_used: ClassVar[List[str]] = [
        "ISU_CD",
        "ISU_SRT_CD",
        "ISU_NM",
        "ISU_ABBRV",
        "ISU_ENG_NM",
        "LIST_DD",
        "MKT_TP_NM",
        "SECUGRP_NM",
        "SECT_TP_NM",
        "KIND_STKCERT_TP_NM",
        "PARVAL",
        "LIST_SHRS",
    ]

    NAME: ClassVar[str] = "basicinfo"

    def __init__(self) -> None:
        pass

    def is_empty(self, json_) -> bool:
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
                csvwriter.writerow(["date"] + BasicInfoClass.key_used)
            # for line_ in csvItems:
            csvwriter.writerows(csvItems)

    def to_csv(self, json_, date_: date) -> None:
        items_ = []
        str_date = date_.strftime("%Y-%m-%d")
        items_raw = json_["OutBlock_1"]

        def parse_to_number(x: str):
            try:
                return int(x.replace(",", ""))
            except ValueError:
                return x

        for item_raw in items_raw:
            [item_raw[key] for key in BasicInfoClass.key_used]
            item_ = [str_date] + [parse_to_number(item_raw[key]) for key in BasicInfoClass.key_used]
            items_.append(item_)
        self.save_to_csv(items_)

    def _make_url_make_url_make_url(
        self, markets: List[str], from_: date, to_: date
    ) -> Generator[str, None, None]:
        buyer_url = URL_ENDPOINT(for_="basic_info")
        for market in markets:
            for date_ in get_weekday(from_=from_, to_=to_):
                YYYYMMDD = date_.strftime("%Y%m%d")
                yield buyer_url.build_url(market, start_date=YYYYMMDD, end_date=YYYYMMDD)

    async def get_data_get_data_get_data(self, markets: List[str], from_: date, to_: date):
        dates_ = get_weekday(from_=from_, to_=to_)
        for endpoint, date_ in zip(
            self._make_url_make_url_make_url(markets, from_=from_, to_=to_), dates_
        ):
            async with aiohttp.ClientSession(headers={"Accept": "application/json"}) as session:
                async with session.post(endpoint) as response:
                    if response.status != 200:
                        # TODO : log it
                        continue
                    # NOTE: 서버측에서 html 형태로 보내서 text으로 처리해야하는 부분이 있음
                    html = await response.text()
                    try:
                        a = json.loads(html)
                        if self.is_empty(a):
                            print("empty!!")
                            # TODO : log it
                            continue
                    except Exception as e:
                        # TODO : handle error
                        print("empty!!")
                        print(e)
                        continue
                    # with open(f"./test-buyers.json", mode="w", encoding="utf-8") as fp:
                    #     json.dump(a, fp, ensure_ascii=False, indent=4)

                    # self.to_csv(a, date_)
                    with open("kosdaq.json", mode="w", encoding="utf-8") as fp:
                        json.dump(a, fp, indent=4, ensure_ascii=False)

            await asyncio.sleep(1.5)
        return

    def _make_url(self, market: str, at_day: date) -> str:
        buyer_url = URL_ENDPOINT(for_="basic_info")
        YYYYMMDD = at_day.strftime("%Y%m%d")
        return buyer_url.build_url(market, start_date=YYYYMMDD, end_date=YYYYMMDD)

    async def get_data(self, market: str, at_day: date) -> List:
        """
        시장 하나 + 한 날짜에 대해서만 가져오기
        """
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
        return a["OutBlock_1"]

    async def run(self, markets: List[str]) -> Coroutine:
        print("run 1")
        await self.get_data(markets=markets, from_=get_today(), to_=get_today())
        print("run 2")
        return 123

    def trim_data(self, json_) -> List:
        items_ = []

        """     
        "ISU_CD": "KR7095570008" → "ISU_CODE"
        "ISU_SRT_CD": "095570" → "ISU_CODE_KR"
        "ISU_NM": "AJ네트웍스보통주" → "ISU_NAME"
        "ISU_ABBRV": "AJ네트웍스" → "ISU_NAME_SHORT"
        "ISU_ENG_NM": "AJ Networks Co.,Ltd." → "ISU_NAME_ENG"
        "LIST_DD": "2015/08/21" → "LISTED_DATE"
        "MKT_TP_NM": "KOSPI" → "MARKET_TYPE_NAME"
        "SECUGRP_NM": "주권" → "SECURITY_GROUP_NAME"
        "SECT_TP_NM": "" → "SECTOR_TYPE_NAME"
        "KIND_STKCERT_TP_NM": "보통주" → "KIND_STKCERT_TYPE_NAME"
        """

        keys = {
            "ISU_CD": "ISU_CODE",
            "ISU_SRT_CD": "ISU_CODE_KR",
            "ISU_NM": "ISU_NAME",
            "ISU_ABBRV": "ISU_NAME_SHORT",
            "ISU_ENG_NM": "ISU_NAME_ENG",
            "LIST_DD": "LISTED_DATE",
            "MKT_TP_NM": "MARKET_TYPE_NAME",
            "SECUGRP_NM": "SECURITY_GROUP_NAME",
            "SECT_TP_NM": "SECTOR_TYPE_NAME",
            "KIND_STKCERT_TP_NM": "KIND_STKCERT_TYPE_NAME",
        }

        for item_raw in json_:
            # item_ = {v: item_raw[k] for k, v in keys.items()}
            item_raw["LIST_DD"] = "-".join(item_raw["LIST_DD"].split("/"))
            item_ = [item_raw[k] for k, v in keys.items()]
            item_.append(f"summary of {item_raw['ISU_ABBRV']}")
            item_.append(1)
            items_.append(item_)
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
        INSERT INGNORE INTO Stock_Info(
            ISU_CODE,
            ISU_CODE_KR,
            ISU_NAME,
            ISU_NAME_SHORT,
            ISU_NAME_ENG,
            LISTED_DATE,
            MARKET_TYPE_NAME,
            SECURITY_GROUP_NAME,
            SECTOR_TYPE_NAME,
            KIND_STKCERT_TYPE_NAME, 
            SUMMARY, 
            STATE_CODE) VALUES (%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s, %s)
        """
        # async with conn.cursor() as curr:
        #     await curr.executemany(insert_query, data_)
        try:
            async with conn.cursor() as curr:
                await curr.executemany(insert_query, data_)
        except Exception as e:
            pprint(data_)
            print(e)
            exit()
        finally:
            conn.close()

    async def run_routine(self) -> None:
        for market in MARKETS.ALL:
            raw_data = await self.get_data(market=market, at_day=get_today())
            data_ = self.trim_data(raw_data)
            await self.insert_data(data_=data_)


"""
SECT_TP_NM --> 이거는 코스피 종목에는 없음

"ISU_CD": "KR7095570008" → "ISU_CODE"
"ISU_SRT_CD": "095570" → "ISU_CODE_KR"
"ISU_NM": "AJ네트웍스보통주" → "ISU_NAME"
"ISU_ABBRV": "AJ네트웍스" → "ISU_ABBRV"
"ISU_ENG_NM": "AJ Networks Co.,Ltd." → "ISU_NAME_ENG"
"LIST_DD": "2015/08/21" → "LISTED_DATE"
"MKT_TP_NM": "KOSPI" → "MARKET_TYPE_NAME"
"SECUGRP_NM": "주권" → "SECURITY_GROUP_NAME"
"SECT_TP_NM": "" → "SECTOR_TYPE_NAME"
"KIND_STKCERT_TP_NM": "보통주" → "KIND_STKCERT_TYPE_NAME"
"PARVAL": "1,000" → "PARVAL"
"LIST_SHRS": "46,822,295" → "LISTED_SHARES"

"ISU_CD": "KR7095570008" → "ISU_CODE"
"ISU_SRT_CD": "095570" → "ISU_CODE_KR"
"ISU_NM": "AJ네트웍스보통주" → "ISU_NAME"
"ISU_ABBRV": "AJ네트웍스" → "ISU_ABBRV"
"ISU_ENG_NM": "AJ Networks Co.,Ltd." → "ISU_NAME_ENG"
"LIST_DD": "2015/08/21" → "LISTED_DATE"
"MKT_TP_NM": "KOSPI" → "MARKET_TYPE_NAME"
"SECUGRP_NM": "주권" → "SECURITY_GROUP_NAME"
"SECT_TP_NM": "" → "SECTOR_TYPE_NAME"
"KIND_STKCERT_TP_NM": "보통주" → "KIND_STKCERT_TYPE_NAME"

# 안쓰는거
"PARVAL": "1,000" → "PARVAL"
"LIST_SHRS": "46,822,295" → "LISTED_SHARES"
"""

if __name__ == "__main__":
    pass

    import asyncio

    loop = asyncio.get_event_loop()
    loop.run_until_complete(BasicInfoClass().run_routine())
    # loop.run_until_complete(
    #     BasicInfoClass().get_data_get_data_get_data(
    #         [MARKETS.KOSDAQ], date(2022, 11, 7), date(2022, 11, 7)
    #     )
    # )

    # for x in BuyerClass()._make_urls(["krx"], date(2022, 10, 23), date(2022, 10, 28)):
    #     print(x)
