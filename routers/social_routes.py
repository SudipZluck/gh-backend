from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from models.user import User
from models.social import UserFollows, UserBlocks
from schemas.social import (
    UserFollowRequest,
    UserBlockRequest,
    UserFollowResponse,
    UserBlockResponse,
)
from security.dependencies import get_current_user
from db.sqlmodel import get_session
from schemas.common import APIResponse

router = APIRouter(prefix="/social", tags=["social"])


@router.post("/follow", response_model=APIResponse[UserFollowResponse])
async def follow_user(
    follow_request: UserFollowRequest,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    if follow_request.following_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot follow yourself",
        )

    existing_follow = session.exec(
        select(UserFollows)
        .where(
            UserFollows.follower_id == current_user.id,
            UserFollows.following_id == follow_request.following_id,
        )
    ).first()

    if existing_follow:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You are already following this user",
        )

    follow = UserFollows(
        follower_id=current_user.id, following_id=follow_request.following_id
    )
    session.add(follow)
    session.commit()
    session.refresh(follow)
    return APIResponse(
        message="User followed successfully",
        data=follow,
        success=True,
        status="success",
        code=status.HTTP_201_CREATED,
    )


@router.delete("/unfollow/{following_id}", response_model=APIResponse)
async def unfollow_user(
    following_id: int,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    follow = session.exec(
        select(UserFollows).where(
            UserFollows.follower_id == current_user.id,
            UserFollows.following_id == following_id,
        )
    ).first()

    if not follow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not following this user",
        )

    session.delete(follow)
    session.commit()
    return APIResponse(
        message="User unfollowed successfully",
        data={},
        success=True,
        status="success",
        code=status.HTTP_200_OK,
    )


@router.post("/block", response_model=APIResponse[UserBlockResponse])
async def block_user(
    block_request: UserBlockRequest,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    if block_request.blocked_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot block yourself",
        )

    existing_block = session.exec(
        select(UserBlocks)
        .where(
            UserBlocks.blocker_id == current_user.id,
            UserBlocks.blocked_id == block_request.blocked_id,
        )
    ).first()

    if existing_block:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already blocked this user",
        )

    block = UserBlocks(
        blocker_id=current_user.id, blocked_id=block_request.blocked_id
    )
    session.add(block)
    session.commit()
    session.refresh(block)
    return APIResponse(
        message="User blocked successfully",
        data=block,
        success=True,
        status="success",
        code=status.HTTP_201_CREATED,
    )


@router.delete("/unblock/{blocked_id}", response_model=APIResponse)
async def unblock_user(
    blocked_id: int,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    block = session.exec(
        select(UserBlocks).where(
            UserBlocks.blocker_id == current_user.id,
            UserBlocks.blocked_id == blocked_id,
        )
    ).first()

    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You have not blocked this user",
        )

    session.delete(block)
    session.commit()
    return APIResponse(
        message="User unblocked successfully",
        data={},
        success=True,
        status="success",
        code=status.HTTP_200_OK,
    )