from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select, func
from models.user import User
from models.journal import (
    Journal,
    Tag,
    JournalReactions,
    JournalFavorites,
    JournalShares,
    JournalReports,
)
from schemas.journal import (
    JournalCreate,
    JournalResponse,
    JournalUpdate,
    JournalReactionCreate,
    JournalReactionResponse,
    JournalFavoriteCreate,
    JournalFavoriteResponse,
    JournalShareCreate,
    JournalShareResponse,
    JournalReportCreate,
    JournalReportResponse,
    JournalFeedResponse,
    JournalFeedUserResponse,
    TagResponse,
)
from security.dependencies import get_current_user
from db.sqlmodel import get_session
from schemas.common import APIResponse

router = APIRouter(prefix="/journals", tags=["journals"])


@router.post("/create", response_model=APIResponse[JournalResponse])
async def create_journal(
    journal_data: JournalCreate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    journal_dict = journal_data.model_dump(exclude={"tags"})
    journal = Journal(**journal_dict, user_id=current_user.id)

    if journal_data.tags:
        for tag_name in journal_data.tags:
            tag = session.exec(select(Tag).where(Tag.name == tag_name)).first()
            if not tag:
                tag = Tag(name=tag_name)
                session.add(tag)
            journal.tags.append(tag)

    session.add(journal)
    session.commit()
    session.refresh(journal)
    return APIResponse(
        message="Journal created successfully",
        data=journal,
    )


@router.get("/get-all", response_model=APIResponse[List[JournalFeedResponse]])
async def get_all_journals(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 10,
):
    # Subquery to count shares for each journal
    share_count_subquery = (
        select(func.count(JournalShares.id))
        .where(JournalShares.journal_id == Journal.id)
        .label("share_count")
    )

    # Subquery to check if the journal is a favorite for the current user
    is_favorite_subquery = (
        select(JournalFavorites.id)
        .where(
            JournalFavorites.journal_id == Journal.id,
            JournalFavorites.user_id == current_user.id,
        )
        .exists()
        .label("is_favorite")
    )

    statement = (
        select(
            Journal
        )
        .options(selectinload(Journal.user), selectinload(Journal.comments), selectinload(Journal.tags))
        .where(Journal.is_deleted == False)
        .offset(skip)
        .limit(limit)
    )
    journals = session.exec(statement).all()

    if not journals:
        return APIResponse(
            message="Journals retrieved successfully",
            data=[],
            success=True,
        )

    journal_ids = [journal.id for journal in journals]

    shares_counts_result = session.exec(
        select(JournalShares.journal_id, func.count(JournalShares.id))
        .where(JournalShares.journal_id.in_(journal_ids))
        .group_by(JournalShares.journal_id)
    ).all()
    shares_map = dict(shares_counts_result)

    user_favorites_result = session.exec(
        select(JournalFavorites.journal_id).where(
            JournalFavorites.journal_id.in_(journal_ids),
            JournalFavorites.user_id == current_user.id,
        )
    ).all()
    favorite_journal_ids = set(user_favorites_result)

    feed = []
    for journal in journals:
        user_data = JournalFeedUserResponse(
            id=journal.user.id,
            name=journal.user.name,
            profile_image_url=journal.user.profile_image_url,
        )

        tags = [TagResponse(id=tag.id, name=tag.name) for tag in journal.tags]

        feed.append(
            JournalFeedResponse(
                id=journal.id,
                user=user_data,
                image_url=journal.image_url,
                title=journal.title,
                body_snippet=journal.body_snippet,
                html_content=journal.html_content,
                created_at=journal.created_at,
                comment_count=len(journal.comments),
                share_count=shares_map.get(journal.id, 0),
                is_favorite=journal.id in favorite_journal_ids,
                tags=tags,
                is_private=journal.is_private,
            )
        )
        feed.sort(key=lambda x: x.created_at, reverse=True)
    return APIResponse(
        message="Journals retrieved successfully",
        data=feed,
        success=True,
    )


@router.get("/tags/{tag_name}", response_model=APIResponse[List[JournalFeedResponse]])
async def get_journals_by_tag(
    tag_name: str,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    tag = session.exec(select(Tag).where(Tag.name == tag_name)).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )

    journals = tag.journals

    feed = []
    for journal in journals:
        user_data = JournalFeedUserResponse(
            id=journal.user.id,
            name=journal.user.name,
            profile_image_url=journal.user.profile_image_url,
        )

        comment_count = len(journal.comments)
        share_count = len(
            session.exec(
                select(JournalShares).where(JournalShares.journal_id == journal.id)
            ).all()
        )
        is_favorite = bool(
            session.exec(
                select(JournalFavorites).where(
                    JournalFavorites.journal_id == journal.id,
                    JournalFavorites.user_id == current_user.id,
                )
            ).first()
        )
        tags = [TagResponse(id=tag.id, name=tag.name) for tag in journal.tags]

        feed.append(
            JournalFeedResponse(
                id=journal.id,
                user=user_data,
                image_url=journal.image_url,
                title=journal.title,
                body_snippet=journal.body_snippet,
                html_content=journal.html_content,
                created_at=journal.created_at,
                comment_count=comment_count,
                share_count=share_count,
                is_favorite=is_favorite,
                tags=tags,
                is_private=journal.is_private,
            )
        )

    return APIResponse(
        message=f"Journals with tag '{tag_name}' retrieved successfully",
        data=feed,
        success=True,
    )


@router.get("/get-user-journals", response_model=APIResponse[List[JournalFeedResponse]])
async def get_user_journals(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 10,
):
    statement = (
        select(Journal)
        .options(selectinload(Journal.user), selectinload(Journal.comments), selectinload(Journal.tags))
        .where(Journal.is_deleted == False, Journal.user_id == current_user.id)
        .order_by(Journal.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    journals = session.exec(statement).all()

    if not journals:
        return APIResponse(
            message="Journals retrieved successfully",
            data=[],
            success=True,
        )

    journal_ids = [journal.id for journal in journals]

    shares_counts_result = session.exec(
        select(JournalShares.journal_id, func.count(JournalShares.id))
        .where(JournalShares.journal_id.in_(journal_ids))
        .group_by(JournalShares.journal_id)
    ).all()
    shares_map = dict(shares_counts_result)

    user_favorites_result = session.exec(
        select(JournalFavorites.journal_id).where(
            JournalFavorites.journal_id.in_(journal_ids),
            JournalFavorites.user_id == current_user.id,
        )
    ).all()
    favorite_journal_ids = set(user_favorites_result)

    feed: List[JournalFeedResponse] = []
    for journal in journals:
        user_data = JournalFeedUserResponse(
            id=journal.user.id,
            name=journal.user.name,
            profile_image_url=journal.user.profile_image_url,
        )
        tags = [TagResponse(id=tag.id, name=tag.name) for tag in journal.tags]

        feed.append(
            JournalFeedResponse(
                id=journal.id,
                user=user_data,
                image_url=journal.image_url,
                title=journal.title,
                body_snippet=journal.body_snippet,
                html_content=journal.html_content,
                created_at=journal.created_at,
                comment_count=len(journal.comments),
                share_count=shares_map.get(journal.id, 0),
                is_favorite=journal.id in favorite_journal_ids,
                tags=tags,
                is_private=journal.is_private,
            )
        )

    return APIResponse(
        message="Journals retrieved successfully",
        data=feed,
        success=True,
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

@router.get("/user/{user_id}", response_model=APIResponse[List[JournalFeedResponse]])
async def get_journals_by_user(
    user_id: int,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 10,
):
    statement = (
        select(Journal)
        .options(selectinload(Journal.user), selectinload(Journal.comments), selectinload(Journal.tags))
        .where(Journal.is_deleted == False, Journal.user_id == user_id)
        .order_by(Journal.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    journals = session.exec(statement).all()

    if not journals:
        return APIResponse(
            message="Journals retrieved successfully",
            data=[],
            success=True,
        )

    journal_ids = [journal.id for journal in journals]

    shares_counts_result = session.exec(
        select(JournalShares.journal_id, func.count(JournalShares.id))
        .where(JournalShares.journal_id.in_(journal_ids))
        .group_by(JournalShares.journal_id)
    ).all()
    shares_map = dict(shares_counts_result)

    user_favorites_result = session.exec(
        select(JournalFavorites.journal_id).where(
            JournalFavorites.journal_id.in_(journal_ids),
            JournalFavorites.user_id == current_user.id,
        )
    ).all()
    favorite_journal_ids = set(user_favorites_result)

    feed: List[JournalFeedResponse] = []
    for journal in journals:
        user_data = JournalFeedUserResponse(
            id=journal.user.id,
            name=journal.user.name,
            profile_image_url=journal.user.profile_image_url,
        )
        tags = [TagResponse(id=tag.id, name=tag.name) for tag in journal.tags]

        feed.append(
            JournalFeedResponse(
                id=journal.id,
                user=user_data,
                image_url=journal.image_url,
                title=journal.title,
                body_snippet=journal.body_snippet,
                html_content=journal.html_content,
                created_at=journal.created_at,
                comment_count=len(journal.comments),
                share_count=shares_map.get(journal.id, 0),
                is_favorite=journal.id in favorite_journal_ids,
                tags=tags,
                is_private=journal.is_private,
            )
        )

    return APIResponse(
        message="Journals retrieved successfully",
        data=feed,
        success=True,
    )


@router.get("/my", response_model=APIResponse[List[JournalFeedResponse]])
async def get_my_journals(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 10,
):
    statement = (
        select(Journal)
        .options(selectinload(Journal.user), selectinload(Journal.comments), selectinload(Journal.tags))
        .where(Journal.is_deleted == False, Journal.user_id == current_user.id)
        .order_by(Journal.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    journals = session.exec(statement).all()

    if not journals:
        return APIResponse(
            message="Journals retrieved successfully",
            data=[],
            success=True,
        )

    journal_ids = [journal.id for journal in journals]

    shares_counts_result = session.exec(
        select(JournalShares.journal_id, func.count(JournalShares.id))
        .where(JournalShares.journal_id.in_(journal_ids))
        .group_by(JournalShares.journal_id)
    ).all()
    shares_map = dict(shares_counts_result)

    user_favorites_result = session.exec(
        select(JournalFavorites.journal_id).where(
            JournalFavorites.journal_id.in_(journal_ids),
            JournalFavorites.user_id == current_user.id,
        )
    ).all()
    favorite_journal_ids = set(user_favorites_result)

    feed: List[JournalFeedResponse] = []
    for journal in journals:
        user_data = JournalFeedUserResponse(
            id=journal.user.id,
            name=journal.user.name,
            profile_image_url=journal.user.profile_image_url,
        )
        tags = [TagResponse(id=tag.id, name=tag.name) for tag in journal.tags]

        feed.append(
            JournalFeedResponse(
                id=journal.id,
                user=user_data,
                image_url=journal.image_url,
                title=journal.title,
                body_snippet=journal.body_snippet,
                html_content=journal.html_content,
                created_at=journal.created_at,
                comment_count=len(journal.comments),
                share_count=shares_map.get(journal.id, 0),
                is_favorite=journal.id in favorite_journal_ids,
                tags=tags,
                is_private=journal.is_private,
            )
        )

    return APIResponse(
        message="Journals retrieved successfully",
        data=feed,
        success=True,
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