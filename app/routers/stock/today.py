from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from urllib import parse
from pprint import pprint

__all__ = ["router"]

router = APIRouter(prefix="/general")


from typing import Optional


@router.get(path="/today", description="코스피, 코스닥, 코넥스 주식 가져오는거")
# async def get_market(db: Session = Depends(deps.get_db), market: str = "KOSPI", limit: int = 50):
async def get_market():
    search_word = parse.unquote(search_word)
    print(search_word)
    # return 200
    queryy = f"""
    SELECT ISU_CODE, ISU_NAME, ISU_NAME_SHORT
    FROM finance.Stock_Info
    WHERE TRADE_DATE='2022-11-22' AND (
        SELECT ISU_CODE
        FROM finance.Stock_Info
        WHERE MARKET_TYPE_NAME='{market}'
    )
    ORDER BY TRADE_VOLUME DESC
    limit 50
    """
    # pprint(queryy)
    try:
        result = db.execute(queryy)
    except Exception as e:
        print(e)
        return "500"
    else:
        return result.fetchall()
    return 200

    return db.execute(aaa).fetchall()


@router.get("/stock/{CODE}")
# async def get_stock(db: Session = Depends(deps.get_db)):
async def get_stock():
    return {"stock": 123}
    try:
        result = db.execute(sql_search)
    except Exception as e:
        print(e)
        return 500
    else:
        return result.fetchall()
