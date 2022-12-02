from dataclasses import dataclass
from fastapi import HTTPException, status

from typing import Optional, Dict, Any, ClassVar, Mapping
from starlette.requests import Request

__all__ = ["UsernameAlreadyExists", "UsernameAgainstPolicy"]


@dataclass
class Username:
    @dataclass
    class alreadyExists:
        msg: ClassVar[str] = "username already exists"
        status_code: ClassVar[int] = status.HTTP_406_NOT_ACCEPTABLE

    @dataclass
    class againstPolicy:
        msg: ClassVar[str] = "Not satisfying username policy"
        status_code: ClassVar[int] = status.HTTP_406_NOT_ACCEPTABLE


class UsernameAlreadyExists(HTTPException):
    def __init__(self, detail: str = Username.alreadyExists.msg, headers: Mapping[str, str] = None):
        super().__init__(Username.alreadyExists.status_code, detail, headers)


class UsernameAgainstPolicy(HTTPException):
    def __init__(self, detail: str = Username.againstPolicy.msg, headers: Mapping[str, str] = None):
        super().__init__(Username.againstPolicy.status_code, detail, headers)
