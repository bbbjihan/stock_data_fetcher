from dataclasses import dataclass
from fastapi import HTTPException, status

from typing import Optional, Dict, Any, ClassVar, Mapping
from starlette.requests import Request


@dataclass
class URLQuery:
    @dataclass
    class notEnough:
        msg: ClassVar[str] = "not enough parameters"
        status_code: ClassVar[int] = status.HTTP_422_UNPROCESSABLE_ENTITY


class NotEnoughQueryParams(HTTPException):
    def __init__(
        self,
        status_code: int = URLQuery.notEnough.status_code,
        detail: str = URLQuery.notEnough.msg,
        headers: Mapping[str, str] = None,
    ):
        super().__init__(status_code, detail, headers)
