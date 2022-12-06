from dataclasses import dataclass
from fastapi import HTTPException, status

from typing import Optional, Dict, Any, ClassVar, Mapping
from starlette.requests import Request

__all__ = ["CredentialsException", "UserNotFound"]


@dataclass
class CredentialsExcept:

    Msg: ClassVar[str] = "Could not validate credentials"
    Headers: ClassVar[Mapping[str, str]] = {"WWW-Authenticate": "Bearer"}


class CredentialsException(HTTPException):
    def __init__(
        self,
        detail: str = CredentialsExcept.Msg,
        headers: Mapping[str, str] = CredentialsExcept.Headers,
    ):
        status_code = status.HTTP_401_UNAUTHORIZED
        super().__init__(status_code, detail, headers)

    def to_dict(self):
        return {
            "status_code": self.status_code,
            "code": "code",
            "msg": self.msg,
            "detail": "detail",
        }


@dataclass
class Users:
    @dataclass
    class notFound:
        msg = "user not found"
        status_code: ClassVar[int] = status.HTTP_404_NOT_FOUND


class UserNotFound(HTTPException):
    def __init__(self, detail: str = Users.notFound.msg, headers: Mapping[str, str] = None) -> None:
        super().__init__(Users.notFound.status_code, detail, headers)
