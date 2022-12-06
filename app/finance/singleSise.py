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
    get_datetime_strfmt,
)
import os, csv
import asyncio
from abc import *
from typing import Coroutine, List, ClassVar, Any, Generator
import aiohttp
import json
import csv
import aiomysql

sise_endpoints = URL_ENDPOINT(for_="single_sise")
from pprint import pprint

# from finance.abstractClass import KRX_data_interface
from abstractClass import KRX_data_interface
import asyncmy

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

    @property
    def column_headers(self) -> List[str]:
        return ["datetime"] + SingelSiseClass.key_used

    """
    date,TDD_CLSPRC,FLUC_TP_CD,CMPPREVDD_PRC,FLUC_RT,TDD_OPNPRC,TDD_HGPRC,TDD_LWPRC,ACC_TRDVOL,ACC_TRDVAL,MKTCAP,LIST_SHRS
    2022-11-09,62000,1,200,0.32,62000,62200,61300,14045592,869644724000,370126518100000,5969782550
    2022-11-08,61800,1,1600,2.66,60500,61900,60500,18273898,1123976801804,368932561590000,5969782550
    2022-11-07,60200,1,800,1.35,59700,60300,59400,12437246,747350127100,359380909510000,5969782550
    """
    """
    2022-11-09 12:32:22 | KR7005930003 | 62000
    
    """

    @property
    def column_dataTypes(self) -> List[str]:
        pass

    def save_to_csv(self, csvItems: List[List[Any]]) -> None:
        """
        write or append data~
        """
        _exists = _file_exists(self.csv_path)

        _mode = "a" if _exists else "w"

        with open(self.csv_path, mode=_mode, encoding="utf-8", newline="") as fp:
            csvwriter = csv.writer(fp)
            if not _exists:
                csvwriter.writerow(self.column_headers)
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
            str_datetime = get_datetime_strfmt()
            item_ = [str_datetime] + [
                parse_to_number(item_raw[key]) for key in SingelSiseClass.key_used
            ]
            items_.append(item_)
            print(item_raw["TDD_CLSPRC"])

        # pprint(items_)
        self.save_to_csv(items_)

    def _make_url(self, ISU_CD: str, from_: date, to_: date) -> str:
        sise_endpoints = URL_ENDPOINT(for_="single_sise")
        date_from = from_.strftime("%Y%m%d")
        date_to = to_.strftime("%Y%m%d")

        # for ISU_CD in ISU_CDs:
        return sise_endpoints.build_url(isuCd=ISU_CD, start_date=date_from, end_date=date_to)

    async def get_data(self, ISU_CD: str, from_: date, to_: date):

        endpoint = self._make_url(ISU_CD, from_=from_, to_=to_)

        # print(f"{endpoint=}")
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
                # self.to_csv(a)
        # with open(f"./test-sise-2022.json", mode="w", encoding="utf-8") as fp:
        #     json.dump(a, fp, ensure_ascii=False, indent=4)
        return a["output"]
        await asyncio.sleep(0.2)

    async def execute_q(self, query):
        conn = await asyncmy.connect(
            host="127.0.0.1",
            port=3309,
            user="root",
            password="mysql-db",
            db="finance",
            autocommit=False,
        )

        async with conn.cursor() as curr:
            await curr.execute(query)
            r = await curr.fetchall()
            print(r)

    def trim_data(self, json_, ISU_CODE) -> List:
        items_ = []

        """     
        "TRD_DD": "2022/11/22", -> TRADE_DATE
        "TDD_CLSPRC": "60,600", -> CLOSE_PRICE
        # "FLUC_TP_CD": "2", -> FLUCTUATION_TYPE_CODE
        "CMPPREVDD_PRC": "-800", -> COMPARED_PREV_PRICE
        "FLUC_RT": "-1.30", -> COMPARED_PREV_RATE
        "TDD_OPNPRC": "60,900", -> OPEN_PRICE
        "TDD_HGPRC": "61,200", -> HIGH_PRICE
        "TDD_LWPRC": "60,300", -> LOW_PRICE
        "ACC_TRDVOL": "9,411,289", -> TRADE_VOLUME
        "ACC_TRDVAL": "571,460,562,800", -> TRADE_VALUE
        "MKTCAP": "361,768,822,530,000", -> MARKET_CAP
        "LIST_SHRS": "5,969,782,550" -> LISTED_SHARES
        """

        # "TRD_DD": "TRADE_DATE",
        keys = {
            "TRD_DD": "TRADE_DATE",
            "TDD_CLSPRC": "CLOSE_PRICE",
            "TDD_OPNPRC": "OPEN_PRICE",
            "TDD_HGPRC": "HIGH_PRICE",
            "TDD_LWPRC": "LOW_PRICE",
            "CMPPREVDD_PRC": "COMPARED_PREV_PRICE",
            "FLUC_RT": "COMPARED_PREV_RATE",
            "ACC_TRDVOL": "TRADE_VOLUME",
            "ACC_TRDVAL": "TRADE_VALUE",
            "MKTCAP": "MARKET_CAP",
            "LIST_SHRS": "LISTED_SHARES",
        }

        # date_ = at_day.strftime("%Y-%m-%d")

        def parse_to_number(x: str):
            try:
                return int(x.replace(",", ""))
            except ValueError:
                try:
                    return float(x)
                except:
                    return x

        for item_raw in json_:
            # print("=" * 10 + "item_raw" + "=" * 10)
            # pprint(item_raw)
            item_raw["TRD_DD"] = "-".join(item_raw["TRD_DD"].split("/"))
            item_ = [ISU_CODE]
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
        INSERT INGNORE INTO Stock_Day_Summary(
            ISU_CODE,
            TRADE_DATE,
            CLOSE_PRICE,
            OPEN_PRICE,
            HIGH_PRICE,
            LOW_PRICE,
            COMPARED_PREV_PRICE,
            COMPARED_PREV_RATE,
            TRADE_VOLUME,
            TRADE_VALUE,
            MARKET_CAP,
            LISTED_SHARES) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        # async with conn.cursor() as curr:
        #     await curr.executemany(insert_query, data_)
        try:
            async with conn.cursor() as curr:
                await curr.executemany(insert_query, data_)
        except Exception as e:
            # pprint(data_)
            # pprint(insert_query)
            # pprint(data_[0])
            print(e)
            exit()
        finally:
            conn.close()

    async def run(self, ISU_CODEs: List[str]) -> Coroutine:

        await self.get_data(["KR7005930003"], date(2022, 11, 3), date(2022, 11, 9))
        # await self.execute_q("select 10")

        return 123

    async def get_isu(self, market):

        conn = await asyncmy.connect(
            host="127.0.0.1",
            port=3309,
            user="root",
            password="mysql-db",
            db="finance",
            autocommit=True,
        )
        Q_query = f"""
        SELECT ISU_CODE FROM Stock_Info
        WHERE MARKET_TYPE_NAME = "{market}"
        """
        # LIMIT 100
        try:
            async with conn.cursor() as curr:
                await curr.execute(Q_query)
                result = await curr.fetchall()
        except Exception as e:
            # pprint(data_)
            print(e)
            exit()
        finally:
            conn.close()
        from itertools import chain

        result = [x for x in chain(*result)]
        # pprint(result)
        return result

    async def run_routine(self) -> None:
        date_ = get_today()
        date_ = date(2022, 11, 22)

        from_ = date(2015, 11, 23)
        # from_ = date(2022, 10, 22)
        to_ = date(2022, 11, 23)

        # return
        for market, market_name in [
            (MARKETS.KOSPI, "KOSPI"),
            (MARKETS.KOSDAQ, "KOSDAQ"),
            (MARKETS.KONEX, "KONEX"),
        ]:
            for isu_code in await self.get_isu(market_name):
                print(f"searching {isu_code} at {market_name}")
                raw_data = await self.get_data(ISU_CD=isu_code, from_=from_, to_=to_)
                if raw_data is None:
                    await asyncio.sleep(1.2)
                    continue
                data_ = self.trim_data(raw_data, isu_code)
                await self.insert_data(data_=data_)
                await asyncio.sleep(1.6)


if __name__ == "__main__":
    pass

    loop = asyncio.get_event_loop()
    ssc = SingelSiseClass()

    loop.run_until_complete(ssc.run_routine())
    # loop.run_until_complete(ssc.get_isu())
    # loop.run_until_complete(
    #     SingelSiseClass().get_data(["KR7005930003"], date(2015, 1, 1), date(2022, 11, 22))
    # )
