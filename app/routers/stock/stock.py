from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

__all__ = ["router"]

router = APIRouter(prefix="/items")

aaa = """
SELECT COUNT(*) as count, MKT_TP_NM as market_name
FROM finance.stock
group by `MKT_TP_NM`
"""

연속하락 = """
SELECT date, ISU_CD, FLUC_RT
FROM finance.stockinfo
WHERE FLUC_RT < 0
ORDER BY date DESC
"""

연속상승 = """
SELECT date, ISU_CD, FLUC_RT
FROM finance.stockinfo
WHERE FLUC_RT > 0
ORDER BY date DESC
"""

"""
금융투자, 보험, 투신, 사모, 은행, 기타금융, 연기금 등, 기관합계, 기타법인, 개인, 외국인, 기타 외국인
종목 별 거래
"""


@router.get("/")
async def temp(db: Session = Depends(deps.get_db)):
    try:
        result = db.execute(aaa)
    except Exception as e:
        print(e)
        return "500"
    else:
        return result.fetchall()
    return 200

    return db.execute(aaa).fetchall()


@router.get("/stock/{CODE}")
async def get_stock(db: Session = Depends(deps.get_db)):
    return {"stock": 123}
    try:
        result = db.execute(sql_search)
    except Exception as e:
        print(e)
        return 500
    else:
        return result.fetchall()
