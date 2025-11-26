from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

from app.domain.schemas.enums import Sections, MissionTypes, MissionStatuses, MissionOrigins

if TYPE_CHECKING:
    from app.db.sql.models.crawler import MissionCrawler
    from app.db.sql.models.operator import MissionOperators
    from app.db.sql.models.platform import MissionPlatform, MissionPlatformRt
    from app.db.sql.models.station import MissionStation


class Mission(SQLModel, table=True):
    __tablename__ = 'missions'

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, nullable=False)
    section: Sections = Field(nullable=False)
    type: MissionTypes = Field(nullable=False)
    status: MissionStatuses = Field(nullable=False)
    origin: MissionOrigins = Field(nullable=False)

    scheduled_start_time: datetime = Field(nullable=False)
    scheduled_end_time: Optional[datetime] = Field(default=None, nullable=False)
    actual_end_time: Optional[datetime] = Field(default=None, nullable=True)

    # Relationships
    mission_operators: List["MissionOperators"] = Relationship(
        back_populates="mission",
        sa_relationship_kwargs={"lazy": "selectin", "cascade": "all, delete"}
    )
    mission_stations: List["MissionStation"] = Relationship(
        back_populates="mission",
        sa_relationship_kwargs={"lazy": "selectin", "cascade": "all, delete"}
    )
    mission_crawlers: List["MissionCrawler"] = Relationship(
        back_populates="mission",
        sa_relationship_kwargs={"lazy": "selectin", "cascade": "all, delete"}
    )
    mission_platforms: List["MissionPlatform"] = Relationship(
        back_populates="mission",
        sa_relationship_kwargs={"lazy": "selectin", "cascade": "all, delete"}
    )
    links: List["MissionPlatformRt"] = Relationship(
        back_populates="mission",
        sa_relationship_kwargs={"lazy": "selectin", "cascade": "all, delete"}
    )
