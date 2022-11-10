from __future__ import annotations
from datetime import date
from finance.utils import (
    URL_ENDPOINT,
    sleep_safe_blocking,
    get_weekday,
    MARKETS,
    date_logging,
    make_file_paths,
    _file_exists,
)
import os, csv
import json

from typing import Coroutine, List, ClassVar, Any, Generator
import aiohttp
from finance.abstractClass import KRX_data_interface
import csv

# 코스피, ETF 포함
# etf=EF
# etn=EN
# elw=EW


class BuyerClass(KRX_data_interface):

    key_used: ClassVar[List[str]] = [
        "INVST_TP_NM",
        "ASK_TRDVOL",
        "BID_TRDVOL",
        "NETBID_TRDVOL",
        "ASK_TRDVAL",
        "BID_TRDVAL",
        "NETBID_TRDVAL",
    ]

    NAME: ClassVar[str] = "buyer"

    def __init__(self) -> None:
        pass

    def is_empty(self, json_) -> bool:
        cnt = 0
        if "output" not in json_.keys():
            return True
        for itmes_ in json_["output"]:
            cnt += [v for k, v in itmes_.items()].count("0")
            if cnt >= 78:
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
                csvwriter.writerow(["date"] + BuyerClass.key_used)
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
            [item_raw[key] for key in BuyerClass.key_used]
            item_ = [str_date] + [
                parse_to_number(item_raw[key]) for key in BuyerClass.key_used
            ]
            items_.append(item_)
        self.save_to_csv(items_)

    def _make_url(
        self, markets: List[str], from_: date, to_: date
    ) -> Generator[str, None, None]:
        buyer_url = URL_ENDPOINT(for_="buyer")
        for market in markets:
            for date_ in get_weekday(from_=from_, to_=to_):
                YYYYMMDD = date_.strftime("%Y%m%d")
                yield buyer_url.build_url(
                    market, start_date=YYYYMMDD, end_date=YYYYMMDD
                )

    async def get_data(self, markets: List[str], from_: date, to_: date):
        dates_ = get_weekday(from_=from_, to_=to_)
        for endpoint, date_ in zip(
            self._make_url(markets, from_=from_, to_=to_), dates_
        ):
            async with aiohttp.ClientSession(
                headers={"Accept": "application/json"}
            ) as session:
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


if __name__ == "__main__":
    pass

    import asyncio

    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        BuyerClass().get_data(["STK"], date(2022, 9, 9), date(2022, 9, 9))
    )
    # for x in BuyerClass()._make_urls(["krx"], date(2022, 10, 23), date(2022, 10, 28)):
    #     print(x)
