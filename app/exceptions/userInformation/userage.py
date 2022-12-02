from dataclasses import dataclass
from fastapi import HTTPException, status

from typing import Optional, Dict, Any, ClassVar, Mapping
from starlette.requests import Request

__all__ = ["TooYoung"]


@dataclass
class UserAge:
    @dataclass
    class notAcceptable:
        msg: ClassVar[str] = "18세 미만은 가입이 불가능합니다 애송이"
        status_code: ClassVar[int] = status.HTTP_406_NOT_ACCEPTABLE


class TooYoung(HTTPException):
    def __init__(self, detail: str = UserAge.notAcceptable.msg, headers: Mapping[str, str] = None):
        super().__init__(UserAge.notAcceptable.status_code, detail, headers)
