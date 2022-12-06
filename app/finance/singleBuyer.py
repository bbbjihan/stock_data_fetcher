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

TLQKF = [("KR7300720000", date(2018, 8, 6)), ("KR7306200007", date(2018, 10, 5))]


class SingelBuyerClass(KRX_data_interface):
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

    @property
    def column_headers(self) -> List[str]:
        return ["datetime"] + SingelSiseClass.key_used

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

    def _make_url(self, ISU_CD: str, at_day: date) -> str:
        sise_endpoints = URL_ENDPOINT(for_="single_buyer")
        YYYYMMDD = at_day.strftime("%Y%m%d")

        # for ISU_CD in ISU_CDs:
        return sise_endpoints.build_url(isuCd=ISU_CD, start_date=YYYYMMDD, end_date=YYYYMMDD)

    async def get_data(self, ISU_CD: str, at_day: date):

        endpoint = self._make_url(ISU_CD, at_day=at_day)
        # return
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
        # with open(f"./test-single-buyer-2022.json", mode="w", encoding="utf-8") as fp:
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

    def trim_data(self, json_, at_day, ISU_CODE) -> List:
        items_ = []

        """     
        "INVST_TP_NM": "금융투자", -> INVEST_TYPE
        "ASK_TRDVOL": "7,911,362", 매도 수량
        "BID_TRDVOL": "8,954,112", 매수 수량 
        "NETBID_TRDVOL": "1,042,750", 순매수 수량 
        "ASK_TRDVAL": "267,243,207,679", 매도 금액
        "BID_TRDVAL": "370,036,886,785", 매수 금액
        "NETBID_TRDVAL": "102,793,679,106", 순매수 금액
        "CONV_OBJ_TP_CD": "" -> 안씀
        """

        # "TRD_DD": "TRADE_DATE",
        keys = {
            "INVST_TP_NM": "INVEST_TYPE",
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
            item_ = [date_, ISU_CODE]
            item_ += [parse_to_number(item_raw[k]) for k, v in keys.items()]
            items_.append(item_)
        # print(f"{len(items_)=}")
        return items_

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
        INSERT IGNORE INTO Stock_Day_Buyers(
            TRADE_DATE,
            ISU_CODE,
            INVEST_TYPE,
            SELL_VOLUME,
            BUY_VOLUME,
            NET_BUY_VOLUME,
            SELL_VALUE,
            BUY_VALUE,
            NET_BUY_VALUE) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
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

        ### 9개, 각각 평균 16시간
        Q_query = f"""
        SELECT ISU_CODE, LISTED_DATE
        FROM 
            finance.Stock_Info
        where 
            market_type_name ="KOSPI" AND
            listed_date >='2019-1-1'
        """  # 74개

        Q_query_ok = f"""
        SELECT ISU_CODE, LISTED_DATE
        FROM 
            finance.Stock_Info
        where 
            market_type_name ="KOSPI" AND
            listed_date >='2012-1-1' AND
            listed_date < '2019-1-1'
        """  # 115개

        Q_query_ok = f"""
        SELECT ISU_CODE, LISTED_DATE
        FROM 
            finance.Stock_Info
        where 
            market_type_name ="KOSPI" AND
            listed_date >= '2007-1-1' AND
            listed_date < '2012-1-1'
        """  # 113개
        Q_query_ok = f"""
        SELECT ISU_CODE, LISTED_DATE
        FROM 
            finance.Stock_Info
        where 
            market_type_name ="KOSPI" AND
            listed_date >= '2000-1-1' AND
            listed_date < '2007-1-1'
        """  # 111개
        Q_query_ok = f"""
        SELECT ISU_CODE, LISTED_DATE
        FROM 
            finance.Stock_Info
        where 
            market_type_name ="KOSPI" AND
            listed_date >= '1992-1-1' AND
            listed_date <= '2000-1-1'
        """  # 119개

        Q_query_ok = f"""
        SELECT ISU_CODE, LISTED_DATE
        FROM 
            finance.Stock_Info
        where 
            market_type_name ="KOSPI" AND
            listed_date >= '1989-6-1' AND
            listed_date < '1992-1-1' 
        """  # 118개

        Q_query_ok = f"""
        SELECT ISU_CODE, LISTED_DATE
        FROM 
            finance.Stock_Info
        where 
            market_type_name ="KOSPI" AND
            listed_date >= '1987-1-1'  AND
            listed_date < '1989-6-1' 
        """  # 95개

        Q_query_ok = f"""
        SELECT ISU_CODE, LISTED_DATE
        FROM 
            finance.Stock_Info
        where 
            market_type_name ="KOSPI" AND
            listed_date >= '1976-1-1' AND
            listed_date < '1987-1-1'  
        """  # 106개

        Q_query_ok = f"""
        SELECT ISU_CODE, LISTED_DATE
        FROM 
            finance.Stock_Info
        where 
            market_type_name ="KOSPI" AND
            listed_date < '1976-1-1'
        """  # 90개

        try:
            async with conn.cursor() as curr:
                await curr.execute(Q_query)
                result = await curr.fetchall()
        except Exception as e:
            pprint(Q_query)
            print(e)
            exit()
        finally:
            conn.close()
        from itertools import chain

        result = [x for x in chain(result)]
        # print(result)
        # exit()
        # pprint(result)
        return result

    async def get_open_day(self):

        conn = await asyncmy.connect(
            host="127.0.0.1",
            port=3309,
            user="root",
            password="mysql-db",
            db="finance",
            autocommit=True,
        )

        Q_query = f"""
        SELECT TRADE_DATE FROM finance.Stock_Day_Summary
        WHERE ISU_CODE="HK0000057197"
        """
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

        result = [x[0] for x in chain(result)]
        # pprint(result)
        return result

    async def run_routine(self) -> None:

        from_ = date(2015, 1, 1)
        # from_ = date(2022, 10, 22)
        to_ = date(2022, 11, 22)

        # return
        # for market, market_name in [
        #     (MARKETS.KOSPI, "KOSPI"),
        #     (MARKETS.KOSDAQ, "KOSDAQ"),
        #     (MARKETS.KONEX, "KONEX"),
        # ]:

        open_days = await self.get_open_day()
        open_days_num = len(open_days)
        for market, market_name in [
            (MARKETS.KOSDAQ, "KOSDAQ"),
        ]:
            num = 1942

            isus = await self.get_isu(market_name)
            search_isu_num = len(isus)
            for i, (isu_code, listed_date) in enumerate(TLQKF, start=1):

                # for isu_code in TLQKF:
                # from_I = listed_date if from_ < listed_date else from_
                from_I = listed_date
                for ii, at_day in enumerate(get_weekday(from_=from_I, to_=to_)):
                    if at_day not in open_days:
                        continue

                    print(
                        f"({i}/{search_isu_num}) searching {isu_code} at {market_name} | {at_day} ... {ii}/{open_days_num}"
                    )
                    raw_data = await self.get_data(ISU_CD=isu_code, at_day=at_day)

                    if raw_data is None:
                        await asyncio.sleep(0.12)
                        continue
                    data_ = self.trim_data(raw_data, at_day, isu_code)
                    # pprint(data_)
                    # return
                    await self.insert_data(data_=data_)
                    await asyncio.sleep(0.12)
                    # return


if __name__ == "__main__":
    pass

    loop = asyncio.get_event_loop()
    ssc = SingelBuyerClass()

    # loop.run_until_complete(ssc.get_open_day())
    loop.run_until_complete(ssc.run_routine())
    # loop.run_until_complete(ssc.get_isu())
    # loop.run_until_complete(
    #     SingelSiseClass().get_data(["KR7005930003"], date(2015, 1, 1), date(2022, 11, 22))
    # )
