from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.domain.schemas.resources import (
    StationRead, CrawlerRead, PlatformRead,
    OperatorRead, RoleRead, RtRead
)


class BaseEventSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    start_time: datetime
    end_time: Optional[datetime] = None

    @model_validator(mode='after')
    def validate_times(self) -> 'BaseEventSchema':
        if self.end_time and self.start_time >= self.end_time:
            raise ValueError('Event end_time must be after start_time')
        return self


# ==========================================
# MISSION STATIONS
# ==========================================
class MissionStationCreate(BaseEventSchema):
    station_id: int


class MissionStationUpdate(BaseModel):
    id: int
    station_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class MissionStationRead(BaseEventSchema):
    id: int
    mission_id: int
    station_id: int
    station: Optional[StationRead] = None


# ==========================================
# MISSION CRAWLERS
# ==========================================
class MissionCrawlerCreate(BaseEventSchema):
    crawler_id: int


class MissionCrawlerUpdate(BaseModel):
    id: int
    crawler_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class MissionCrawlerRead(BaseEventSchema):
    id: int
    mission_id: int
    crawler_id: int
    crawler: Optional[CrawlerRead] = None


# ==========================================
# MISSION OPERATORS
# ==========================================
class MissionOperatorCreate(BaseEventSchema):
    operator_id: int
    role_id: int


class MissionOperatorUpdate(BaseModel):
    id: int
    operator_id: Optional[int] = None
    role_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class MissionOperatorRead(BaseEventSchema):
    id: int
    mission_id: int
    operator_id: int
    role_id: int
    operator: Optional[OperatorRead] = None
    role: Optional[RoleRead] = None


# ==========================================
# MISSION PLATFORMS
# ==========================================
class MissionPlatformCreate(BaseEventSchema):
    platform_id: int
    main_rt_num: Optional[int] = None
    backup_rt_num: Optional[int] = None
    pod_num: Optional[int] = None
    rass_num: Optional[int] = None
    atru_num: Optional[int] = None


class MissionPlatformUpdate(BaseModel):
    id: int
    platform_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    main_rt_num: Optional[int] = None
    backup_rt_num: Optional[int] = None
    pod_num: Optional[int] = None
    rass_num: Optional[int] = None
    atru_num: Optional[int] = None


class MissionPlatformRead(BaseEventSchema):
    id: int
    mission_id: int
    platform_id: int
    main_rt_num: Optional[int] = None
    backup_rt_num: Optional[int] = None
    pod_num: Optional[int] = None
    rass_num: Optional[int] = None
    atru_num: Optional[int] = None

    platform: Optional[PlatformRead] = None
    # We can include RT details if needed
    main_rt: Optional[RtRead] = None
    backup_rt: Optional[RtRead] = None


# ==========================================
# MISSION PLATFORM RTs
# ==========================================
class MissionPlatformRtBase(BaseEventSchema):
    is_active: bool
    up_channel: int = Field(..., ge=0, le=9)
    down_channel: int = Field(..., ge=0, le=9)


class MissionPlatformRtCreate(MissionPlatformRtBase):
    platform_id: int
    rt_num: int


class MissionPlatformRtUpdate(BaseModel):
    id: int
    rt_num: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_active: Optional[bool] = None
    up_channel: Optional[int] = None
    down_channel: Optional[int] = None


class MissionPlatformRtRead(MissionPlatformRtBase):
    id: int
    mission_id: int
    platform_id: int
    rt_num: int
    rt: Optional[RtRead] = None
    platform: Optional[PlatformRead] = None


class BatchEventUpdate[CreateT, UpdateT](BaseModel):
    mission_id: int
    creates: List[CreateT] = []
    updates: List[UpdateT] = []
    deletes: List[int] = []  # IDs to delete
    auto_fix_gaps: bool = True


BatchStationUpdate = BatchEventUpdate[MissionStationCreate, MissionStationUpdate]
BatchCrawlerUpdate = BatchEventUpdate[MissionCrawlerCreate, MissionCrawlerUpdate]
BatchPlatformUpdate = BatchEventUpdate[MissionPlatformCreate, MissionPlatformUpdate]
BatchRtUpdate = BatchEventUpdate[MissionPlatformRtCreate, MissionPlatformRtUpdate]
BatchOperatorUpdate = BatchEventUpdate[MissionOperatorCreate, MissionOperatorUpdate]
