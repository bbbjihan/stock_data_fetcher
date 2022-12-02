from fastapi import APIRouter, Depends, status, Query, WebSocket, Body

from sqlalchemy.orm import Session
from urllib import parse
from pprint import pprint
from routers.dep import get_db
from typing import Optional, List, Union, Any, Mapping
from pydantic import BaseModel, PositiveInt, Field

__all__ = ["router", "websocket_endpoint"]

router = APIRouter(prefix="/post")
from uuid import uuid4, UUID
from enum import Enum
import itertools
from datetime import date, datetime


class PostTextFrom(BaseModel):
    """
    게시글 내용 중 텍스트 부분
    """

    text: str
    pass


class PostMediaFrom(BaseModel):
    """
    게시글 내용 중 이미지, 동영상
    """

    file_name: str
    pass


class PostData(BaseModel):
    """
    게시글 데이터 포맷 여러개의 TextForm과 MeidaForm이 존재한다.
    JSON 내에 리스트는 불안정하니 "1" : { ... }
    """

    upload_date: date = Field(default_factory=date)
    postID: UUID = Field(default_factory=uuid4)
    data: Mapping[int, Union[PostMediaFrom, PostTextFrom]]
    pass


@router.get("")
async def list_post(db: Session = Depends(get_db)):
    """
    게시판 글 가져오는거
    """
    pass


@router.post("")
async def make_post(db: Session = Depends(get_db)):
    """
    게시판 글 작성
    """
    pass


@router.patch("")
async def update_post(db: Session = Depends(get_db)):
    """
    게시판 글 수정
    """
    pass


@router.delete("")
async def delete_posts(db: Session = Depends(get_db)):
    """
    게시판 글 삭제
    """
    pass
