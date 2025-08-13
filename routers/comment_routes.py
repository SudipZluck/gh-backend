from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from models.user import User
from models.comment import Comment
from schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from security.dependencies import get_current_user
from db.sqlmodel import get_session
from schemas.common import APIResponse

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("/", response_model=APIResponse[CommentResponse])
async def create_comment(
    comment_data: CommentCreate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    comment = Comment(**comment_data.model_dump(), user_id=current_user.id)
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return APIResponse(
        message="Comment created successfully",
        data=comment,
        success=True,
        status="success",
        code=status.HTTP_201_CREATED,
    )


@router.get("/{journal_id}", response_model=APIResponse[List[CommentResponse]])
async def get_comments_for_journal(
    journal_id: int,
    session: Annotated[Session, Depends(get_session)],
    skip: int = 0,
    limit: int = 10,
):
    comments = session.exec(
        select(Comment)
        .where(Comment.journal_id == journal_id, Comment.is_deleted == False)
        .offset(skip)
        .limit(limit)
    ).all()
    return APIResponse(
        message="Comments retrieved successfully",
        data=comments,
        success=True,
        status="success",
        code=status.HTTP_200_OK,
    )


@router.put("/{comment_id}", response_model=APIResponse[CommentResponse])
async def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    comment = session.get(Comment, comment_id)
    if not comment or comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    comment.text = comment_data.text
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return APIResponse(
        message="Comment updated successfully",
        data=comment,
        success=True,
        status="success",
        code=status.HTTP_200_OK,
    )


@router.delete("/{comment_id}", response_model=APIResponse)
async def delete_comment(
    comment_id: int,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    comment = session.get(Comment, comment_id)
    if not comment or comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    comment.is_deleted = True
    session.add(comment)
    session.commit()

    return APIResponse(
        message="Comment deleted successfully",
        data={},
        success=True,
        status="success",
        code=status.HTTP_200_OK,
    )