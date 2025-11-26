from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field

from app.domain.schemas.enums import Sections, MissionTypes, MissionStatuses, MissionOrigins
from app.domain.schemas.events import (
    MissionStationRead,
    MissionCrawlerRead,
    MissionPlatformRead,
    MissionOperatorRead,
    MissionPlatformRtRead
)


class MissionBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    section: Sections
    type: MissionTypes
    status: MissionStatuses
    origin: MissionOrigins
    scheduled_start_time: datetime
    scheduled_end_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None


class MissionCreate(MissionBase):
    pass


class MissionUpdate(BaseModel):
    name: Optional[str] = None
    section: Optional[Sections] = None
    type: Optional[MissionTypes] = None
    status: Optional[MissionStatuses] = None
    origin: Optional[MissionOrigins] = None
    scheduled_start_time: Optional[datetime] = None
    scheduled_end_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None


class MissionRead(MissionBase):
    id: int

    stations: List[MissionStationRead] = Field(default_factory=list, alias="mission_stations")
    crawlers: List[MissionCrawlerRead] = Field(default_factory=list, alias="mission_crawlers")
    platforms: List[MissionPlatformRead] = Field(default_factory=list, alias="mission_platforms")
    operators: List[MissionOperatorRead] = Field(default_factory=list, alias="mission_operators")
    links: List[MissionPlatformRtRead] = Field(default_factory=list)

    class Config:
        populate_by_name = True
