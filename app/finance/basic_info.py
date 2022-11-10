from __future__ import annotations
import requests
from datetime import date, datetime, timezone, timedelta
from finance.utils import (
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
import os, csv
import json

from abc import *
from typing import Coroutine, List, ClassVar, Any, Generator
import aiohttp

import csv

from finance.abstractClass import KRX_data_interface


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

    def _make_url(self, markets: List[str], from_: date, to_: date) -> Generator[str, None, None]:
        buyer_url = URL_ENDPOINT(for_="basic_info")
        for market in markets:
            for date_ in get_weekday(from_=from_, to_=to_):
                YYYYMMDD = date_.strftime("%Y%m%d")
                yield buyer_url.build_url(market, start_date=YYYYMMDD, end_date=YYYYMMDD)

    async def get_data(self, markets: List[str], from_: date, to_: date):
        dates_ = get_weekday(from_=from_, to_=to_)
        for endpoint, date_ in zip(self._make_url(markets, from_=from_, to_=to_), dates_):
            async with aiohttp.ClientSession(headers={"Accept": "application/json"}) as session:
                async with session.post(endpoint) as response:
                    if response.status != 200:
                        # TODO : log it
                        continue
                    # print("Status:", response.status)
                    # print("Content-type:", response.headers["content-type"])
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
                    self.to_csv(a, date_)

            sleeped = sleep_safe_blocking(1.5, 2)
        return

    async def run(self, markets: List[str]) -> Coroutine:
        return await self.get_data(markets=markets, from_=get_today(), to_=get_today())


if __name__ == "__main__":
    pass

    import asyncio

    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        BasicInfoClass().get_data(["KNX"], date(2022, 11, 7), date(2022, 11, 7))
    )
    # for x in BuyerClass()._make_urls(["krx"], date(2022, 10, 23), date(2022, 10, 28)):
    #     print(x)
