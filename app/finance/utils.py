from dataclasses import dataclass
from typing import List, Optional, Generator
from datetime import date, timedelta, datetime, timezone
import os
import random
import time
from typing import ClassVar
from pprint import pprint


@dataclass(frozen=True)
class MARKETS:
    KOSPI: ClassVar[str] = "STK"
    KOSDAQ: ClassVar[str] = "KSQ"
    KONEX: ClassVar[str] = "KNX"
    ALL: ClassVar[List[str]] = ["KNX", "KSQ", "STK"]
    PROGRAM: ClassVar[List[str]] = ["KSQ", "STK"]


@dataclass
class URL_ENDPOINT:
    _BASE_URL: ClassVar[str] = "https://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"
    _REQUIRED_QUERY: ClassVar[str] = "csvxls_isNo=false&locale=ko_KR"
    _API_TYPE: ClassVar[str] = "bld=dbms/MDC/STAT/standard/{}"
    _VARY: ClassVar[dict] = {
        "program": {"API_TYPE": "MDCSTAT02601", "typical": "share=2&money=3"},
        "stockInfo": {"API_TYPE": "MDCSTAT01501", "typical": "share=1&money=1"},
        "buyer": {
            "API_TYPE": "MDCSTAT02201",
            "typical": "inqTpCd=1&trdVolVal=2&askBid=3&share=2&money=3",
        },
        "basic_info": {"API_TYPE": "MDCSTAT01901", "typical": "share=1"},
        "single_sise": {
            "API_TYPE": "MDCSTAT01701",
            "typical": "share=1&money=1&adjStkPrc_check=Y&adjStkPrc=2",
        },
        "single_buyer": {
            "API_TYPE": "MDCSTAT02301",
            "typical": "inqTpCd=1&trdVolVal=2&askBid=3&share=1&money=1",
        },
    }

    _MARKET_TYPE: ClassVar[str] = "mktId={}"  # STK, KSQ, KNX
    _START_DATE: ClassVar[str] = "strtDd={}"  # 20221014 - program, buyer
    _END_DATE: ClassVar[str] = "endDd={}"  # 20221014 - program, buyer
    _TRADE_DATE: ClassVar[str] = "trdDd={}"  # 20221014 - stock
    _STOCK_CODE: ClassVar[str] = "isuCd={}"  # KR7005930003 - single_sise, single_buyer

    for_: str  # program, stockInfo, buyer, basic_info

    def build_url(
        self,
        /,
        market_type: str = None,
        start_date: str = None,
        end_date: str = None,
        trade_date: str = None,
        isuCd: str = None,
    ):
        """
        Args:
            market_type (str): STK, KSQ, KNX
            start_date (str, optional): 2022-10-26 -> "20221026" - program, buyer, single_sise, single_buyer
            end_date (str, optional): 2022-10-26 -> "20221026" - program, buyer, single_sise, single_buyer
            trade_date (str, optional): 2022-10-26 -> "20221026" - stock
            isuCd (str) : "KR7005930003" - single_sise ISU_CD(필수)
        Returns:
            str: URL endpoint
        """
        url_build = f"{self._BASE_URL}?"
        url_build += f'{self._API_TYPE.format(self._VARY[self.for_]["API_TYPE"])}'
        url_build += f'&{self._VARY[self.for_]["typical"]}'
        url_build += f"&{self._REQUIRED_QUERY}"
        url_build += f"&{self._MARKET_TYPE.format(market_type)}"
        if start_date:
            url_build += f"&{self._START_DATE.format(start_date)}"
        if end_date:
            url_build += f"&{self._END_DATE.format(end_date)}"
        if trade_date:
            url_build += f"&{self._TRADE_DATE.format(trade_date)}"
        if isuCd:
            url_build += f"&{self._STOCK_CODE.format(isuCd)}"
        return url_build


def get_weekday(from_: date, to_: date) -> Generator[date, None, None]:
    oneday = timedelta(days=1)
    x = from_
    # 토요일 = 5, 일요일 = 6
    while True:
        if x.weekday() not in (5, 6):
            yield x
            # yield x.strftime("%Y%m%d")
        if x < to_:
            x += oneday
        elif x >= to_:
            break
    return


def get_today() -> date:
    TZ_KST = timezone(timedelta(hours=9), "KST")
    return datetime.now(tz=TZ_KST).date()


def get_datetime_strfmt() -> datetime:
    TZ_KST = timezone(timedelta(hours=9), "KST")
    return datetime.now(tz=TZ_KST).strftime("%Y-%m-%d %H:%M:%S")


def date_logging(from_: date, to_: date, now_, market):
    print(
        f"{market} | starting From {from_.strftime('%Y-%m-%d')} ... to {to_.strftime('%Y-%m-%d')} | {now_}"
    )


def _file_exists(path_: os.PathLike) -> bool:
    return os.path.exists(path_)


def make_file_paths(file_path: os.PathLike):
    dir_path = os.path.dirname(file_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def sleep_safe_blocking(min: float = 1.0, max: float = 3.0):
    tt = min + (max - min) * random.random()
    time.sleep(tt)
    return tt


if __name__ == "__main__":
    prgm_url = URL_ENDPOINT("program")
    stock_url = URL_ENDPOINT("stockInfo")
    buyer_url = URL_ENDPOINT("buyer")

    a = prgm_url.build_url("STK", "20221026", "20221026")
    a = stock_url.build_url("KNX", trade_date="20221026")
    a = buyer_url.build_url("KNX", end_date="20221026", start_date="20221026")
    # import requests

    # with requests.post(a) as resp:
    #     print(f"{resp.status_code=}")
    #     pprint(resp.json())
