from fastapi import APIRouter, Depends, status, Query, WebSocket, Body

from sqlalchemy.orm import Session
from urllib import parse
from pprint import pprint
from routers.dep import get_db
from typing import Optional, List, Union, Any
from pydantic import BaseModel, PositiveInt

__all__ = ["router", "websocket_endpoint"]

router = APIRouter(prefix="/topic")

from enum import Enum
import itertools


class MARKET_TYPE(Enum):
    KOSPI = "KOSPI"
    KOSDAQ = "KOSDAQ"
    KOSDAQ_GLOBAL = "KOSDAQ GLOBAL"
    KONEX = "KONEX"


class STOCK_STATE_CODE(Enum):
    NORMAL: int = 1


class SearchStatParams(BaseModel):
    rise_in_row: Optional[PositiveInt]
    fall_in_row: Optional[PositiveInt]
    price_over: Optional[PositiveInt]
    price_under: Optional[PositiveInt]
    market_type: Optional[MARKET_TYPE]
    stock_type_name: Optional[str]
    market_cap_over: Optional[PositiveInt]
    market_cap_under: Optional[PositiveInt]
    trade_volume_over: Optional[PositiveInt]
    trade_volume_under: Optional[PositiveInt]
    trade_value_over: Optional[PositiveInt]
    trade_value_under: Optional[PositiveInt]
    fluc_rate_over: Optional[float]
    fluc_rate_under: Optional[float]
    fluc_price_over: Optional[PositiveInt]
    fluc_price_under: Optional[PositiveInt]
    days: Optional[PositiveInt]


class SearchQueryResult(BaseModel):
    ISU_CODE: str
    ISU_CODE_KR: str
    ISU_NAME: str
    ISU_NAME_SHORT: str
    MARKET_TYPE_NAME: MARKET_TYPE
    STATE_CODE: STOCK_STATE_CODE


class SearchQueryResponse(BaseModel):
    asked: Optional[SearchStatParams]
    result: Optional[List[SearchQueryResult]]


# @router.get("/a", response_model=Union[SearchQueryResponse, Any])
@router.get("/a")
async def in_seq(searchParams: SearchStatParams = Body(None), db: Session = Depends(get_db)):
    """
    어제 종가 기준으로 ~일 연속으로 하락/상승한 종목
    """
    # print(searchParams)
    days = 5
    price_up = ">"
    target_market = "KOSPI"
    queryy = f"""
    SELECT ISU_CODE
    FROM (
        SELECT
        ISU_CODE,
        count(coalesce(cnt, 1)=1 OR null) OVER (PARTITION BY tmp3.ISU_CODE ORDER BY tmp3.TRADE_DATE ASC) seq
        FROM (
            SELECT
                data_days.ISU_CODE,
                data_days.TRADE_DATE,
                if(data_days.COMPARED_PREV_PRICE {price_up} 0, 1, 0) as cnt
            FROM (
                (SELECT SI.ISU_CODE
                FROM finance.Stock_Info as SI
                WHERE SI.MARKET_TYPE_NAME="{target_market}") filtered 
                INNER JOIN (
                    SELECT *
                    FROM finance.Stock_Day_Summary as SDS
                    WHERE SDS.TRADE_DATE IN (
                        SELECT * FROM (
                            SELECT * 
                            FROM finance.Business_Day
                            ORDER BY `day` DESC
                            limit {days}
                        ) as tmp
                    )
                ) data_days
                ON filtered.ISU_CODE = data_days.ISU_CODE
            )
        ) as tmp3
    ) as tmp4
    WHERE seq = {days}
    """
    # pprint(queryy)
    searchResults = db.execute(queryy).fetchall()
    ISO_CODEs = [*itertools.chain(*searchResults)]
    # pprint(ISO_CODEs)
    return {"ISO_CODE": ISO_CODEs}


# @router.get("/b", response_model=Union[SearchQueryResponse, Any])
@router.get("/b")
async def in_seq_date_between(
    searchParams: SearchStatParams = Body(None), db: Session = Depends(get_db)
):
    """
    A 일부터 B 일까지 연속으로 하락/상승한 종목
    """
    print(searchParams)
    date_from = "2022-10-15"
    date_to = "2022-10-22"
    price_up = ">"
    target_market = "KOSPI"

    queryy = f"""
    START TRANSACTION; 
    DROP TEMPORARY TABLE IF EXISTS tmp3;
    DROP TEMPORARY TABLE IF EXISTS tlqkf;
    
    CREATE TEMPORARY TABLE tlqkf(
        SELECT
            data_days.ISU_CODE,
            data_days.TRADE_DATE,
            data_days.CLOSE_PRICE,
            data_days.HIGH_PRICE,
            data_days.LOW_PRICE,
            if(data_days.COMPARED_PREV_PRICE {price_up} 0, 1, 0) as cnt
        FROM (
            (SELECT SI.ISU_CODE, SI.ISU_NAME, SI.ISU_NAME_SHORT, SI.SUMMARY
            FROM finance.Stock_Info as SI
            WHERE SI.MARKET_TYPE_NAME="{target_market}") filtered 
            INNER JOIN (
                SELECT *
                FROM finance.Stock_Day_Summary as SDS
                WHERE SDS.TRADE_DATE IN (
                    SELECT * FROM (
                        SELECT * 
                        FROM finance.Business_Day
                        WHERE `day` >= '{date_from}' AND `day` <= '{date_to}'
                        ORDER BY `day` DESC
                    ) as tmp
                )
            ) data_days ON filtered.ISU_CODE = data_days.ISU_CODE )
    );

    CREATE TEMPORARY TABLE tmp3(
        SELECT ISU_CODE,TRADE_DATE,cnt
        FROM tlqkf
    );

    SELECT tlqkf.ISU_CODE, tlqkf.TRADE_DATE, tlqkf.CLOSE_PRICE, tlqkf.HIGH_PRICE, tlqkf.LOW_PRICE FROM (
        (SELECT tmp5.ISU_CODE
        FROM (
            SELECT
            tmp3.ISU_CODE,
            count(coalesce(cnt, 1)=1 OR null) OVER (PARTITION BY tmp3.ISU_CODE ORDER BY tmp3.TRADE_DATE ASC) seq
            FROM tmp3
        ) as tmp5
        WHERE tmp5.seq = (
                SELECT count(*) as days_count
                FROM finance.Business_Day
                WHERE `day` >= '{date_from}' AND `day` <= '{date_to}'
        ))  temptemp
        JOIN tlqkf ON temptemp.ISU_CODE = tlqkf.ISU_CODE
    ) ;

    DROP TEMPORARY TABLE tmp3;
    DROP TEMPORARY TABLE tlqkf;
    COMMIT;
    """
    a = f"""
    CREATE TEMPORARY TABLE tlqkf(
        SELECT
            data_days.ISU_CODE,
            data_days.TRADE_DATE,
            data_days.CLOSE_PRICE,
            data_days.HIGH_PRICE,
            data_days.LOW_PRICE,
            if(data_days.COMPARED_PREV_PRICE {price_up} 0, 1, 0) as cnt
        FROM (
            (SELECT SI.ISU_CODE, SI.ISU_NAME, SI.ISU_NAME_SHORT, SI.SUMMARY
            FROM finance.Stock_Info as SI
            WHERE SI.MARKET_TYPE_NAME="{target_market}") filtered 
            INNER JOIN (
                SELECT *
                FROM finance.Stock_Day_Summary as SDS
                WHERE SDS.TRADE_DATE IN (
                    SELECT * FROM (
                        SELECT * 
                        FROM finance.Business_Day
                        WHERE `day` >= '{date_from}' AND `day` <= '{date_to}'
                        ORDER BY `day` DESC
                    ) as tmp
                )
            ) data_days ON filtered.ISU_CODE = data_days.ISU_CODE )
    );
    """
    b = f"""
    SELECT tlqkf.ISU_CODE, tlqkf.TRADE_DATE, tlqkf.CLOSE_PRICE, tlqkf.HIGH_PRICE, tlqkf.LOW_PRICE FROM (
        (SELECT tmp5.ISU_CODE
        FROM (
            SELECT
            tmp3.ISU_CODE,
            count(coalesce(cnt, 1)=1 OR null) OVER (PARTITION BY tmp3.ISU_CODE ORDER BY tmp3.TRADE_DATE ASC) seq
            FROM tmp3
        ) as tmp5
        WHERE tmp5.seq = (
                SELECT count(*) as days_count
                FROM finance.Business_Day
                WHERE `day` >= '{date_from}' AND `day` <= '{date_to}'
        ))  temptemp
        JOIN tlqkf ON temptemp.ISU_CODE = tlqkf.ISU_CODE
    ) ;"""

    db.execute("DROP TEMPORARY TABLE IF EXISTS tmp3;")
    db.execute("DROP TEMPORARY TABLE IF EXISTS tlqkf;")
    db.execute(a)
    db.execute("CREATE TEMPORARY TABLE tmp3(SELECT ISU_CODE,TRADE_DATE,cnt FROM tlqkf);")
    ss = db.execute(b).fetchall()
    db.execute("DROP TEMPORARY TABLE tmp3;")
    db.execute("DROP TEMPORARY TABLE tlqkf;")
    db.close()
    # pprint(ss)
    isu_codes = set()
    items = {"data": {}}
    for row in ss:
        isu_code, trade_date, close_prc, high_prc, low_prc = row
        isu_codes.add(row[0])
        if items["data"].get(isu_code, None) is None:
            items["data"][isu_code] = [
                {
                    "TRADE_DATE": trade_date,
                    "CLOSE_PRICE": close_prc,
                    "HIGH_PRICE": high_prc,
                    "LOW_PRICE": low_prc,
                }
            ]
        else:
            items["data"][isu_code].append(
                {
                    "TRADE_DATE": trade_date,
                    "CLOSE_PRICE": close_prc,
                    "HIGH_PRICE": high_prc,
                    "LOW_PRICE": low_prc,
                }
            )
    items["ISU_CODE"] = isu_codes
    return items
