from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from models.user import User
from models.journal import Journal, JournalTags, JournalReactions, JournalFavorites, JournalShares, JournalReports
from schemas.journal import JournalCreate, JournalResponse, JournalUpdate, JournalTagCreate, JournalTagResponse, JournalReactionCreate, JournalReactionResponse, JournalFavoriteCreate, JournalFavoriteResponse, JournalShareCreate, JournalShareResponse, JournalReportCreate, JournalReportResponse
from security.dependencies import get_current_user
from db.sqlmodel import get_session
from schemas.common import APIResponse

router = APIRouter(prefix="/journals", tags=["journals"])


@router.post("/", response_model=APIResponse[JournalResponse])
async def create_journal(
    journal_data: JournalCreate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    journal = Journal(**journal_data.model_dump(), user_id=current_user.id)
    session.add(journal)
    session.commit()
    session.refresh(journal)
    return APIResponse(
        message="Journal created successfully",
        data=journal,
        success=True,
        status="success",
        code=status.HTTP_201_CREATED,
    )


@router.get("/", response_model=APIResponse[List[JournalResponse]])
async def get_all_journals(
    session: Annotated[Session, Depends(get_session)],
    skip: int = 0,
    limit: int = 10,
):
    journals = session.exec(
        select(Journal).where(Journal.is_deleted == False).offset(skip).limit(limit)
    ).all()
    return APIResponse(
        message="Journals retrieved successfully",
        data=journals,
        success=True,
        status="success",
        code=status.HTTP_200_OK,
    )


@router.get("/{journal_id}", response_model=APIResponse[JournalResponse])
async def get_journal_by_id(
    journal_id: int,
    session: Annotated[Session, Depends(get_session)],
):
    journal = session.get(Journal, journal_id)
    if not journal or journal.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Journal not found"
        )
    return APIResponse(
        message="Journal retrieved successfully",
        data=journal,
        success=True,
        status="success",
        code=status.HTTP_200_OK,
    )


@router.put("/{journal_id}", response_model=APIResponse[JournalResponse])
async def update_journal(
    journal_id: int,
    journal_data: JournalUpdate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    journal = session.get(Journal, journal_id)
    if not journal or journal.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Journal not found"
        )

    for key, value in journal_data.model_dump(exclude_unset=True).items():
        setattr(journal, key, value)

    session.add(journal)
    session.commit()
    session.refresh(journal)
    return APIResponse(
        message="Journal updated successfully",
        data=journal,
        success=True,
        status="success",
        code=status.HTTP_200_OK,
    )


@router.delete("/{journal_id}", response_model=APIResponse)
async def delete_journal(
    journal_id: int,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    journal = session.get(Journal, journal_id)
    if not journal or journal.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Journal not found"
        )

    journal.is_deleted = True
    journal.deleted_at = "CURRENT_TIMESTAMP"
    session.add(journal)
    session.commit()

    return APIResponse(
        message="Journal deleted successfully",
        data={},
        success=True,
        status="success",
        code=status.HTTP_200_OK,
    )

@router.post("/journal-tags", response_model=APIResponse[JournalTagResponse])
async def create_journal_tag(
    journal_tag_data: JournalTagCreate,
    session: Annotated[Session, Depends(get_session)],
):
    journal_tag = JournalTags(**journal_tag_data.model_dump())
    session.add(journal_tag)
    session.commit()
    session.refresh(journal_tag)
    return APIResponse(
        message="Journal tag created successfully",
        data=journal_tag,
        success=True,
        status="success",
        code=status.HTTP_201_CREATED,
    )


@router.get(
    "/journal-tags/{journal_id}", response_model=APIResponse[List[JournalTagResponse]]
)
async def get_journal_tags(
    journal_id: int,
    session: Annotated[Session, Depends(get_session)],
)-> APIResponse[List[JournalTagResponse]]:
    journal_tags = session.exec(
        select(JournalTags).where(JournalTags.journal_id == journal_id)
    ).all()
    return APIResponse[List[JournalTagResponse]](
        message="Journal tags retrieved successfully",
        data=journal_tags,
        success=True
    )


@router.post(
    "/journal-reactions", response_model=APIResponse[JournalReactionResponse]
)
async def create_journal_reaction(
    journal_reaction_data: JournalReactionCreate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    journal_reaction = JournalReactions(
        **journal_reaction_data.model_dump(), user_id=current_user.id
    )
    session.add(journal_reaction)
    session.commit()
    session.refresh(journal_reaction)
    return APIResponse(
        message="Journal reaction created successfully",
        data=journal_reaction,
        success=True,
        status="success",
        code=status.HTTP_201_CREATED,
    )


@router.get(
    "/journal-reactions/{journal_id}",
    response_model=APIResponse[List[JournalReactionResponse]],
)
async def get_journal_reactions(
    journal_id: int,
    session: Annotated[Session, Depends(get_session)],
):
    journal_reactions = session.exec(
        select(JournalReactions).where(JournalReactions.journal_id == journal_id)
    ).all()
    return APIResponse(
        message="Journal reactions retrieved successfully",
        data=journal_reactions,
        success=True,
        status="success",
        code=status.HTTP_200_OK,
    )


@router.post(
    "/journal-favorites", response_model=APIResponse[JournalFavoriteResponse]
)
async def create_journal_favorite(
    journal_favorite_data: JournalFavoriteCreate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    journal_favorite = JournalFavorites(
        **journal_favorite_data.model_dump(), user_id=current_user.id
    )
    session.add(journal_favorite)
    session.commit()
    session.refresh(journal_favorite)
    return APIResponse(
        message="Journal favorite created successfully",
        data=journal_favorite,
        success=True,
        status="success",
        code=status.HTTP_201_CREATED,
    )


@router.get(
    "/journal-favorites", response_model=APIResponse[List[JournalFavoriteResponse]]
)
async def get_journal_favorites(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    journal_favorites = session.exec(
        select(JournalFavorites).where(JournalFavorites.user_id == current_user.id)
    ).all()
    return APIResponse(
        message="Journal favorites retrieved successfully",
        data=journal_favorites,
        success=True,
        status="success",
        code=status.HTTP_200_OK,
    )


@router.post("/journal-shares", response_model=APIResponse[JournalShareResponse])
async def create_journal_share(
    journal_share_data: JournalShareCreate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    journal_share = JournalShares(
        **journal_share_data.model_dump(), user_id=current_user.id
    )
    session.add(journal_share)
    session.commit()
    session.refresh(journal_share)
    return APIResponse(
        message="Journal share created successfully",
        data=journal_share,
        success=True,
        status="success",
        code=status.HTTP_201_CREATED,
    )


@router.post("/journal-reports", response_model=APIResponse[JournalReportResponse])
async def create_journal_report(
    journal_report_data: JournalReportCreate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    journal_report = JournalReports(
        **journal_report_data.model_dump(), reporter_id=current_user.id
    )
    session.add(journal_report)
    session.commit()
    session.refresh(journal_report)
    return APIResponse(
        message="Journal report created successfully",
        data=journal_report,
        success=True,
        status="success",
        code=status.HTTP_201_CREATED,
    )