from exceptions.auth import *
from dataclasses import dataclass


@dataclass
class ErrorData:
    status_code: int
    dict: dict


class AuthExceptionHandler:
    pass


#     @classmethod
#     def handle(cls, exception: Exception):

#         if isinstance(exception, CredentialsException):
#             pass
#         elif isinstance(exception, UserNotFound):
#             pass
#         elif isinstance(exception, TokenExceptions):
#             pass
#         elif isinstance(exception, TokenMalformed):
#             pass
#         elif isinstance(exception, TokenExpired):
#             pass
#         elif isinstance(exception, TokenDecodeFailed):
#             pass
#         elif isinstance(exception, CredentialsException):
#             pass

#         return ErrorData(exception.status_code, exception.to_dict())
