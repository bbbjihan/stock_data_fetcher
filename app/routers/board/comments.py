from fastapi import APIRouter, Depends, status, Query, WebSocket, Body
from fastapi import UploadFile, File
from sqlalchemy.orm import Session
from urllib import parse
from pprint import pprint
from routers.dep import get_db
from typing import Optional, List, Union, Any
from pydantic import BaseModel, PositiveInt, Field

__all__ = ["router", "websocket_endpoint"]

router = APIRouter(prefix="/comment")

from enum import Enum
import itertools


class PostCommentForm(BaseModel):
    """
    댓글 포맷
    """

    # 1. user id
    # 2.
    pass


@router.get("/:postId")
async def get_comment(postId: Optional[int]):
    """
    게시글에 있는 댓글보기
    """
    return 200


@router.post("")
async def post_comment(postId: Optional[int], commentID: Optional[int]):
    """
    댓글 쓰기
    commentID는 대댓글 달 때 사용됨
    """
    return


@router.post("/up")
async def post_comment_score(postId: Optional[int]):
    """
    댓글 개추
    """
    return


@router.post("/down")
async def post_comment_score(postId: Optional[int]):
    """
    댓글 비추
    """
    return
