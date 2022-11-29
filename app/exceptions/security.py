from dataclasses import dataclass
from fastapi import HTTPException, status

from typing import Optional, Dict, Any, ClassVar, Mapping
from starlette.requests import Request


@dataclass
class CredentialsExcept:

    Msg: ClassVar[str] = "Could not validate credentials"
    Headers: ClassVar[Mapping[str, str]] = {"WWW-Authenticate": "Bearer"}


class CredentialsException(HTTPException):
    def __init__(
        self,
        detail: str = CredentialsExcept.Msg,
        headers: Mapping[str, str] = CredentialsExcept.Headers,
    ) -> None:
        status_code = status.HTTP_401_UNAUTHORIZED
        super().__init__(status_code, detail, headers)


@dataclass
class Tokens:
    @dataclass
    class expired:
        msg: ClassVar[str] = "token expired"
        status_code: ClassVar[int] = status.HTTP_403_FORBIDDEN

    @dataclass
    class decode:
        msg: ClassVar[str] = "token compromised"
        status_code: ClassVar[int] = status.HTTP_400_BAD_REQUEST


class TokenMalformed(HTTPException):
    def __init__(self, detail: str = Tokens.expired.msg, headers: Mapping[str, str] = None) -> None:
        super().__init__(Tokens.expired.status_code, detail, headers)


class TokenExpired(HTTPException):
    def __init__(self, detail: str = Tokens.expired.msg, headers: Mapping[str, str] = None) -> None:
        super().__init__(Tokens.expired.status_code, detail, headers)


class TokenDecodeFailed(HTTPException):
    def __init__(self, detail: str = Tokens.decode.msg, headers: Mapping[str, str] = None) -> None:
        super().__init__(Tokens.decode.status_code, detail, headers)


@dataclass
class Users:
    @dataclass
    class notFound:
        msg = "user not found"
        status_code: ClassVar[int] = status.HTTP_404_NOT_FOUND


class UserNotFound(HTTPException):
    def __init__(self, detail: str = Users.notFound.msg, headers: Mapping[str, str] = None) -> None:
        super().__init__(Users.notFound.status_code, detail, headers)
