from typing import Annotated, List
from fastapi import APIRouter, Depends, status
from sqlalchemy import literal, union_all
from sqlmodel import Session, select
from models.user import User
from models.prompt import Prompts, UserPrompts
from schemas.prompt import (
    PromptCreate,
    PromptResponse,
    UserPromptCreate,
    UserPromptResponse,
)
from security.dependencies import get_current_user
from db.sqlmodel import get_session
from schemas.common import APIResponse

router = APIRouter(prefix="/prompts", tags=["prompts"])


@router.post("/", response_model=APIResponse[PromptResponse])
async def create_prompt(
    prompt_data: PromptCreate,
    session: Annotated[Session, Depends(get_session)],
):
    prompt = Prompts(**prompt_data.model_dump())
    session.add(prompt)
    session.commit()
    session.refresh(prompt)
    return APIResponse(
        message="Prompt created successfully",
        data=prompt,
    )


@router.get("/", response_model=APIResponse[List[PromptResponse]])
async def get_prompts(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    stmt1 = select(
        Prompts.id.label("id"),
        Prompts.text.label("text"),
        literal(None).label("user_id"),   # always null here
        Prompts.is_active.label("is_active"),
        Prompts.created_at.label("created_at")
    )

    # UserPrompts: has user_id
    stmt2 = select(
        UserPrompts.id.label("id"),
        UserPrompts.text.label("text"),
        UserPrompts.user_id.label("user_id"),
        UserPrompts.is_active.label("is_active"),
        UserPrompts.created_at.label("created_at")
    ).where(
            UserPrompts.user_id == current_user.id, UserPrompts.is_active == True
        )

    # Combine with UNION (remove duplicates) or UNION ALL (keep all)
    union_stmt = union_all(stmt1, stmt2)
    prompts = session.exec(union_stmt).all()
    return APIResponse(
        message="Prompts retrieved successfully",
        data=prompts,
    )


@router.post("/user-prompts", response_model=APIResponse[UserPromptResponse])
async def create_user_prompt(
    user_prompt_data: UserPromptCreate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    user_prompt = UserPrompts(
        **user_prompt_data.model_dump(), user_id=current_user.id
    )
    session.add(user_prompt)
    session.commit()
    session.refresh(user_prompt)
    return APIResponse(
        message="User prompt created successfully",
        data=user_prompt,
    )


@router.get("/user-prompts", response_model=APIResponse[List[UserPromptResponse]])
async def get_user_prompts(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    user_prompts = session.exec(
        select(UserPrompts).where(
            UserPrompts.user_id == current_user.id, UserPrompts.is_active == True
        )
    ).all()
    return APIResponse(
        message="User prompts retrieved successfully",
        data=user_prompts,
    )