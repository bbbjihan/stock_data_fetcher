from fastapi import APIRouter, Depends, status, Query, WebSocket, Body, Path

from sqlalchemy.orm import Session
from urllib import parse
from pprint import pprint
from routers.dep import get_db
from typing import Optional, List, Union, Any
from pydantic import BaseModel, NonNegativeInt, PositiveInt
from utils.regex import only_KOR_chosung, only_KOR_char, only_NUM, is_ISU_CODE
from exceptions.urlParams import NotEnoughQueryParams

__all__ = ["router", "websocket_endpoint"]

router = APIRouter(prefix="/search")
from enum import Enum


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


class SearchQueryResult(BaseModel):
    ISU_CODE: str
    ISU_CODE_KR: str
    ISU_NAME: str
    ISU_NAME_SHORT: str
    MARKET_TYPE_NAME: MARKET_TYPE
    STATE_CODE: STOCK_STATE_CODE


class SearchQueryResponse(BaseModel):
    asked: SearchQueryParams
    result: Optional[List[SearchQueryResult]]


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


@router.get("", response_model=SearchQueryResponse)
async def search_by_keyword_or_code(
    searchParams: SearchQueryParams = Body(), db: Session = Depends(get_db)
):
    """
    주식 이름 검색하는 API
    1. 주식 코드 ISU_CODE, ISU_CODE_KR 으로 검색하는 조건
    2. 주식 전체 이름, 축약 이름(일반적으로 부르는거) ISU_NAME, ISU_NAME_SHORT 으로 검색하는 조건
    """
    if not searchParams.dict(exclude_none=True):
        raise NotEnoughQueryParams

    where_clause = optimize_searching(searchParams.keyword)

    if mrkt := searchParams.market:
        MARKET_TYPE.KONEX == mrkt

    queryy = f"""
    SELECT ISU_CODE, ISU_CODE_KR,ISU_NAME, ISU_NAME_SHORT, MARKET_TYPE_NAME, STATE_CODE
    FROM finance.Stock_Info
    WHERE {where_clause}
    """
    if not where_clause:
        # 말도 안되는거 검색하면 쿼리 안하고 끝내기
        return SearchQueryResponse(asked=searchParams, result=[])
    searchResults = db.execute(queryy).fetchall()
    searchResults = [SearchQueryResult(**x) for x in searchResults]
    return SearchQueryResponse(asked=searchParams, result=searchResults)


@router.websocket("/name/ws")
async def search_by_keyword_or_code_websocket(
    websocket: WebSocket, db: Session = Depends(get_db)
) -> None:
    """
    WS에서 유니코드로 보냄
    JS 웹 콘솔 상에서 JSON.parse(a)으로 받으면 정상적으로 사용가능
    """
    await websocket.accept()
    while True:
        searchParam = await websocket.receive_text()
        queryy = f"""
        SELECT ISU_CODE, ISU_CODE_KR,ISU_NAME, ISU_NAME_SHORT, MARKET_TYPE_NAME, STATE_CODE
        FROM finance.Stock_Info
        WHERE 
            ISU_NAME LIKE '%{searchParam}%' OR 
            ISU_NAME_SHORT LIKE '%{searchParam}%' OR 
            ISU_NAME_SHORT_INITIAL LIKE '%{searchParam}%'
        """
        searchResults = db.execute(queryy).fetchall()
        searchResults = [SearchQueryResult(**x) for x in searchResults]
        sqp = SearchQueryParams(keyword=searchParam, stock_code=None)
        sqr = SearchQueryResponse(asked=sqp, result=searchResults)
        await websocket.send_json(sqr.json(), mode="text")


@router.get("/stat", response_model=Union[SearchQueryResponse, Any])
async def search_by(searchParams: SearchStatParams = Body(), db: Session = Depends(get_db)):
    """
    주식 이름 검색하는 API
    1. 주식 코드 ISU_CODE, ISU_CODE_KR 으로 검색하는 조건
    2. 주식 전체 이름, 축약 이름(일반적으로 부르는거) ISU_NAME, ISU_NAME_SHORT 으로 검색하는 조건
    """
    print(searchParams)

    queryy = f"""
    SELECT DISTINCT RD7.ISU_CODE
    FROM finance.Recent_Days_7 as RD7
    INNER JOIN (
        SELECT cnt.ISU_CODE 
        FROM (
            SELECT 
                RD7_.ISU_CODE,
                COUNT(RD7_.COMPARED_PREV_RATE) as rise_in_day_7
            FROM 
                finance.Recent_Days_7 as RD7_
            WHERE
                RD7_.COMPARED_PREV_RATE >= 0
            GROUP BY RD7_.ISU_CODE) as cnt
        WHERE rise_in_day_7 =7) rise_7
    ON RD7.ISU_CODE = rise_7.ISU_CODE
    """
    searchResults = db.execute(queryy).fetchall()
    return searchResults


def optimize_searching(keyword: str) -> str:
    if only_KOR_chosung(keyword):
        return f"ISU_NAME_SHORT_INITIAL LIKE '%{keyword}%'"
    if only_KOR_char(keyword):
        return f"ISU_NAME LIKE '%{keyword}%' or ISU_NAME_SHORT LIKE '%{keyword}%'"
    if only_NUM(keyword) or is_ISU_CODE(keyword):
        return f"ISU_CODE_KR LIKE '%{keyword}%' or ISU_CODE LIKE '%{keyword}%'"
    return
