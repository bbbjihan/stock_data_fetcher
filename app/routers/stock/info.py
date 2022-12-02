from fastapi import APIRouter, Depends, status, Query, WebSocket, Body, Path

from sqlalchemy.orm import Session
from urllib import parse
from pprint import pprint
from routers.dep import get_db
from typing import Optional, List, Union, Any, Mapping
from pydantic import BaseModel, NonNegativeInt, PositiveInt, Field
from utils.regex import only_KOR_chosung, only_KOR_char, only_NUM, is_ISU_CODE
from exceptions.urlParams import NotEnoughQueryParams
from exceptions.requestBody import EmptyRequestBody, NotEnoughRequestBody
from enum import Enum
from datetime import date

router = APIRouter(prefix="")


class MARKET_TYPE(Enum):
    KOSPI = "KOSPI"
    KOSDAQ = "KOSDAQ"
    KOSDAQ_GLOBAL = "KOSDAQ GLOBAL"
    KONEX = "KONEX"


class STOCK_STATE_CODE(Enum):
    NORMAL: int = 1


class SearchQueryParams(BaseModel):
    keyword: Optional[str]
    market: Optional[MARKET_TYPE]


class GetStockInfo(BaseModel):
    ISU_CODE: List[str]

    class Config:
        schema_extra = {"example": {"ISU_CODE": ["KR7000152009"]}}


@router.get("/info")
async def get_stock_general_info(
    isu_code: str = Query(example="KR7000152009", description="주식 ISU CODE"),
    db: Session = Depends(get_db),
):
    """
    주식에 대해서 모든 정보를 가져오는 엔드포인트
    """
    query = f"""
    SELECT 
        ISU_CODE, ISU_CODE_KR, ISU_NAME, ISU_NAME_SHORT, ISU_NAME_ENG,
        LISTED_DATE, MARKET_TYPE_NAME, SECURITY_GROUP_NAME, KIND_STKCERT_TYPE_NAME,
        SUMMARY, STATE_CODE ,SECTOR_TYPE_NAME
    FROM finance.Stock_Info
    where ISU_CODE = "{isu_code}"
    """
    return db.execute(query).fetchone()
    print(f"{isu_code=}")
    return 200


class StockDayPriceInfo(BaseModel):
    TRADE_DATE: date
    CLOSE_PRICE: PositiveInt
    COMPARED_PREV_PRICE: int
    COMPARED_PREV_RATE: float
    TRADE_VOLUME: PositiveInt
    TRADE_VALUE: PositiveInt
    MARKET_CAP: PositiveInt
    LISTED_SHARES: PositiveInt

    @property
    def tradeDate(self):
        return self.TRADE_DATE

    @property
    def priceInfo(self):
        return {
            "CLOSE_PRICE": self.CLOSE_PRICE,
            "COMPARED_PREV_PRICE": self.COMPARED_PREV_PRICE,
            "COMPARED_PREV_RATE": self.COMPARED_PREV_RATE,
            "TRADE_VOLUME": self.TRADE_VOLUME,
            "TRADE_VALUE": self.TRADE_VALUE,
            "MARKET_CAP": self.MARKET_CAP,
            "LISTED_SHARES": self.LISTED_SHARES,
        }

    class Config:
        schema_extra = {
            "example": {
                "CLOSE_PRICE": 88400,
                "COMPARED_PREV_PRICE": -300,
                "COMPARED_PREV_RATE": -0.34,
                "TRADE_VOLUME": 851,
                "TRADE_VALUE": 75680300,
                "MARKET_CAP": 78944559200,
                "LISTED_SHARES": 893038,
            }
        }


class StockDayInfo(StockDayPriceInfo):
    ISU_CODE: str
    ISU_CODE_KR: str
    ISU_NAME: str
    ISU_NAME_SHORT: str
    MARKET_TYPE_NAME: str
    STATE_CODE: PositiveInt

    @property
    def stockInfo(self):
        return {
            "ISU_CODE": self.ISU_CODE,
            "ISU_CODE_KR": self.ISU_CODE_KR,
            "ISU_NAME": self.ISU_NAME,
            "ISU_NAME_SHORT": self.ISU_NAME_SHORT,
            "MARKET_TYPE_NAME": self.MARKET_TYPE_NAME,
            "STATE_CODE": self.STATE_CODE,
        }

    class Config:
        schema_extra = {
            "example": {
                "TRADE_DATE": "2022-11-14",
                "ISU_CODE": "KR7000152009",
                "ISU_CODE_KR": "000157",
                "ISU_NAME": "두산2우선주(신형)",
                "ISU_NAME_SHORT": "두산2우B",
                "MARKET_TYPE_NAME": "KOSPI",
                "STATE_CODE": 1,
                "CLOSE_PRICE": 88400,
                "COMPARED_PREV_PRICE": 200,
                "COMPARED_PREV_RATE": -0.34,
                "TRADE_VOLUME": 851,
                "TRADE_VALUE": 75680300,
                "MARKET_CAP": 78944559200,
                "LISTED_SHARES": 893038,
            }
        }


class GetStockInfoResult(BaseModel):
    count: NonNegativeInt = Field(description="반한되는 StockDayInfo의 개수, 일반적으로 7의 배수")
    data: dict = Field(description="주식 ISU_CODE에 있는 데이터들")
    ISU_CODES: List[str] = Field(default=[], description="ISU_CODE가 있는 리스트")

    class Config:
        schema_extra = {
            "example": {
                "count": 7,
                "data": {
                    "KR7000152009": {
                        "DATES": ["2022-11-22"],
                        "ISU_CODE": "KR7000152009",
                        "ISU_CODE_KR": "000157",
                        "ISU_NAME": "두산2우선주(신형)",
                        "ISU_NAME_SHORT": "두산2우B",
                        "MARKET_TYPE_NAME": "KOSPI",
                        "STATE_CODE": 1,
                        "2022-11-22": {
                            "CLOSE_PRICE": 88000,
                            "COMPARED_PREV_PRICE": 800,
                            "COMPARED_PREV_RATE": 0.92,
                            "TRADE_VOLUME": 3435,
                            "TRADE_VALUE": 306574400,
                            "MARKET_CAP": 78587344000,
                            "LISTED_SHARES": 893038,
                        },
                    }
                },
                "ISU_CODES": ["KR7000152009"],
            }
        }


@router.get("/7days", response_model=GetStockInfoResult)
async def get_stocks_7_days_info(
    getStockInfo: GetStockInfo = Body(), db: Session = Depends(get_db)
):
    """
    주식 이름으로 결과가 여러개 나오고, 상품 목록처럼 보여줄 때
    최근 영업일 7일 동안 주식 가격 보여주는 용도
    """
    if not getStockInfo.ISU_CODE:
        raise EmptyRequestBody
    aa = [f'"{x}"' for x in getStockInfo.ISU_CODE]
    queryy = f"""
    SELECT 
        RD7.TRADE_DATE, 
        RD7.ISU_CODE,
        SearchName.ISU_CODE_KR,
        SearchName.ISU_NAME, 
        SearchName.ISU_NAME_SHORT, 
        SearchName.MARKET_TYPE_NAME, 
        SearchName.STATE_CODE,
        RD7.CLOSE_PRICE,
        RD7.COMPARED_PREV_PRICE,
        RD7.COMPARED_PREV_RATE,
        RD7.TRADE_VOLUME,
        RD7.TRADE_VALUE,
        RD7.MARKET_CAP,
        RD7.LISTED_SHARES
    FROM 
        finance.Recent_Days_7 as RD7
            INNER JOIN
        (SELECT 
            ISU_CODE, ISU_CODE_KR,ISU_NAME, ISU_NAME_SHORT, MARKET_TYPE_NAME, STATE_CODE
        FROM 
            finance.Stock_Info
        WHERE
            ISU_CODE in ({','.join(aa)})) as SearchName ON RD7.ISU_CODE = SearchName.ISU_CODE
    order by RD7.ISU_CODE, RD7.TRADE_DATE
    """
    searchResults = db.execute(queryy).fetchall()
    data_ = {"count": 0, "data": {}}
    isu_codes = set()
    for x in searchResults:
        data_["count"] += 1
        sdi = StockDayInfo(**x)
        isu_codes.add(sdi.ISU_CODE)
        isu_code = sdi.ISU_CODE
        if not data_["data"].get(isu_code, None):
            data_["data"][isu_code] = {}
            data_["data"][isu_code]["DATES"] = []
            data_["data"][isu_code].update(sdi.stockInfo)
        data_["data"][isu_code]["DATES"].append(sdi.tradeDate)
        data_["data"][isu_code][sdi.tradeDate] = sdi.priceInfo
    data_["ISU_CODES"] = list(isu_codes)
    return GetStockInfoResult(**data_)
