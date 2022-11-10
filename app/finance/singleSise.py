from __future__ import annotations
import requests
from datetime import date
from finance.utils import (
    URL_ENDPOINT,
    sleep_safe_blocking,
    get_weekday,
    make_file_paths,
    MARKETS,
    date_logging,
    _file_exists,
)
import os, csv


from abc import *
from typing import Coroutine, List, ClassVar, Any, Generator
import aiohttp
import json
import csv

sise_endpoints = URL_ENDPOINT(for_="single_sise")
from pprint import pprint
from finance.abstractClass import KRX_data_interface

# exit()


class SingelSiseClass(KRX_data_interface):
    "TRD_DD"
    key_used: ClassVar[List[str]] = [
        "TDD_CLSPRC",
        "FLUC_TP_CD",
        "CMPPREVDD_PRC",
        "FLUC_RT",
        "TDD_OPNPRC",
        "TDD_HGPRC",
        "TDD_LWPRC",
        "ACC_TRDVOL",
        "ACC_TRDVAL",
        "MKTCAP",
        "LIST_SHRS",
    ]

    NAME: ClassVar[str] = "single_sise"

    def __init__(self) -> None:
        pass

    def is_empty(self, json_) -> bool:
        if json_["output"] == []:
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
        _exists = _file_exists(self.csv_path)

        _mode = "a" if _exists else "w"

        with open(self.csv_path, mode=_mode, encoding="utf-8", newline="") as fp:
            csvwriter = csv.writer(fp)
            if not _exists:
                csvwriter.writerow(["date"] + SingelSiseClass.key_used)
            csvwriter.writerows(csvItems)

    def to_csv(self, json_) -> None:
        items_ = []
        items_raw = json_["output"]

        def parse_to_number(x: str):
            try:
                return int(x.replace(",", ""))
            except ValueError:
                return x

        # print(f"{len(items_raw)=}")
        for item_raw in items_raw:
            str_date = "-".join(item_raw["TRD_DD"].split("/"))
            item_ = [str_date] + [
                parse_to_number(item_raw[key]) for key in SingelSiseClass.key_used
            ]
            items_.append(item_)
        self.save_to_csv(items_)

    def _make_url(self, ISU_CDs: List[str], from_: date, to_: date) -> str:
        sise_endpoints = URL_ENDPOINT(for_="single_sise")
        date_from = from_.strftime("%Y%m%d")
        date_to = to_.strftime("%Y%m%d")

        for ISU_CD in ISU_CDs:
            yield sise_endpoints.build_url(
                isuCd=ISU_CD, start_date=date_from, end_date=date_to
            )

    async def get_data(self, ISU_CDs: List[str], from_: date, to_: date):
        for endpoint in self._make_url(ISU_CDs, from_=from_, to_=to_):
            # print(f"{endpoint=}")
            async with aiohttp.ClientSession(
                headers={"Accept": "application/json"}
            ) as session:
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
                    self.to_csv(a)
            sleeped = sleep_safe_blocking(1.5, 2)
        return


if __name__ == "__main__":
    pass

    import asyncio

    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        SingelSiseClass().get_data(
            ["KR7005930003"], date(2022, 11, 3), date(2022, 11, 9)
        )
    )
