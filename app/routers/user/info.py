from fastapi import APIRouter
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from urllib import parse
from pprint import pprint
from routers.dep import get_db
from typing import Optional, List, Union, Any
from pydantic import BaseModel, PositiveInt, EmailStr, EmailError, Field, conint, ConstrainedInt
import re
import hashlib
from uuid import uuid4
from datetime import date
from exceptions.userInformation import *

__all__ = ["router"]

router = APIRouter(prefix="/info")


@router.get("")
async def tlqkf():
    return 200
