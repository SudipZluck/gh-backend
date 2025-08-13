from pydantic import BaseModel
from typing import Annotated
from datetime import datetime


class UserFollowRequest(BaseModel):
    following_id: Annotated[int, "The ID of the user to follow"]


class UserBlockRequest(BaseModel):
    blocked_id: Annotated[int, "The ID of the user to block"]


class UserFollowResponse(BaseModel):
    id: int
    follower_id: int
    following_id: int
    created_at: datetime


class UserBlockResponse(BaseModel):
    id: int
    blocker_id: int
    blocked_id: int
    created_at: datetime