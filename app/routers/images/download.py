from fastapi import APIRouter, Depends, status, Query, WebSocket, Body
from fastapi import UploadFile, File
from sqlalchemy.orm import Session
from urllib import parse
from pprint import pprint
from routers.dep import get_db
from typing import Optional, List, Union, Any
from pydantic import BaseModel, PositiveInt, Field

__all__ = ["router", "websocket_endpoint"]

router = APIRouter(prefix="")

from enum import Enum
import itertools


class ImageForm(BaseModel):
    """
    사진
    """

    pass


class PostTextFrom(BaseModel):
    """
    게시글 내용 중 사진부분
    """

    pass


class FileHeaders(BaseModel):

    content_disposition: str = Field(alias="content-disposition")
    name: str


@router.post("/upload")
# async def upload_image(file_: UploadFile):
async def upload_image(file_: List[UploadFile]):
    """
    사진 올리기
    한번에 하나 올리나 여러개 올리나 List으로 받아도 ㄱㅊ
    """
    # file_ = file_[0]
    print(f"{file_[0].filename}")
    # print(f"{file_[1].filename}")
    return 200


@router.get("/test")
async def return_image(files_: List[UploadFile]):
    """
    사진 주기

    """
    return 200


@router.delete("/test")
async def return_image(files_: List[UploadFile]):
    """
    사진 삭제하기
    """
    return 200


def generate_file_info():
    """
    이미지 메타데이터,
    파일 이름->hash,
    파일 위치 생성 후 반환
    """
    pass
