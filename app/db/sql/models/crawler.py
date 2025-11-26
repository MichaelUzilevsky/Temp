from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

from app.domain.schemas.enums import Sites

if TYPE_CHECKING:
    from app.db.sql.models.black import Black
    from app.db.sql.models.mission import Mission


class Crawler(SQLModel, table=True):
    __tablename__ = 'crawlers'

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(
        index=True,
        unique=True,
        nullable=False,
        regex=r"^DirtyDance.*"  # Regex from your screenshot
    )
    site: Sites = Field(nullable=False)
    black_num: Optional[int] = Field(
        default=None,
        foreign_key="blacks.num",
        nullable=False,
        ondelete="CASCADE"
    )

    # Relationships
    black: Optional["Black"] = Relationship(
        back_populates="crawlers",
        sa_relationship_kwargs={"lazy": "selectin"}
    )
    missions: List["MissionCrawler"] = Relationship(
        back_populates="crawler",
        sa_relationship_kwargs={"cascade": "all, delete"}
    )


class MissionCrawler(SQLModel, table=True):
    __tablename__ = 'mission_crawlers'

    id: Optional[int] = Field(default=None, primary_key=True)
    mission_id: int = Field(foreign_key="missions.id", ondelete="CASCADE", index=True)
    crawler_id: int = Field(foreign_key="crawlers.id", ondelete="CASCADE", index=True)
    start_time: datetime = Field(index=True, nullable=False)
    end_time: Optional[datetime] = Field(default=None, nullable=True)

    # Relationships
    mission: "Mission" = Relationship(back_populates="mission_crawlers")
    crawler: "Crawler" = Relationship(
        back_populates="missions",
        sa_relationship_kwargs={"lazy": "selectin"}
    )
