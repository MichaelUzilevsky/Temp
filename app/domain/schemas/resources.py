from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field

from app.domain.schemas.enums import Sites, PlatformTypes, RtLocations, OperatorRolesEnum


# --- Base Configuration ---
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# ==========================================
# BLACKS
# ==========================================
class BlackBase(BaseSchema):
    name: str
    site: Sites


class BlackCreate(BlackBase):
    num: int = Field(..., ge=1, description="Primary Key")


class BlackUpdate(BaseSchema):
    name: Optional[str] = None
    site: Optional[Sites] = None


class BlackRead(BlackBase):
    num: int


# ==========================================
# STATIONS
# ==========================================
class StationBase(BaseSchema):
    name: str
    site: Sites
    black_num: int


class StationCreate(StationBase):
    num: int = Field(..., ge=1, description="Station Number")


class StationUpdate(BaseSchema):
    name: Optional[str] = None
    site: Optional[Sites] = None
    black_num: Optional[int] = None


class StationRead(StationBase):
    num: int
    black: Optional[BlackRead] = None


# ==========================================
# CRAWLERS
# ==========================================
class CrawlerBase(BaseSchema):
    name: str = Field(..., pattern=r"^DirtyDance.*")
    site: Sites
    black_num: Optional[int] = None


class CrawlerCreate(CrawlerBase):
    pass


class CrawlerUpdate(BaseSchema):
    name: Optional[str] = Field(None, pattern=r"^DirtyDance.*")
    site: Optional[Sites] = None
    black_num: Optional[int] = None


class CrawlerRead(CrawlerBase):
    id: int
    black: Optional[BlackRead] = None


# ==========================================
# RTs
# ==========================================
class RtBase(BaseSchema):
    location: RtLocations
    is_main: bool


class RtCreate(RtBase):
    num: int = Field(..., description="RT Number")


class RtUpdate(BaseSchema):
    location: Optional[RtLocations] = None
    is_main: Optional[bool] = None


class RtRead(RtBase):
    num: int


# ==========================================
# PLATFORMS
# ==========================================
class PlatformBase(BaseSchema):
    type: PlatformTypes


class PlatformCreate(PlatformBase):
    tail_num: int = Field(..., ge=100, le=999)


class PlatformUpdate(BaseSchema):
    type: Optional[PlatformTypes] = None


class PlatformRead(PlatformBase):
    tail_num: int


# ==========================================
# ROLES
# ==========================================
class RoleBase(BaseSchema):
    name: OperatorRolesEnum


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseSchema):
    name: Optional[OperatorRolesEnum] = None


class RoleRead(RoleBase):
    id: int


# ==========================================
# OPERATORS
# ==========================================
class OperatorBase(BaseSchema):
    first_name: str
    last_name: str


class OperatorCreate(OperatorBase):
    roles: List[int]


class OperatorUpdate(BaseSchema):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    roles: list[int] = None


class OperatorRead(OperatorBase):
    id: int
    roles: List[RoleRead] = None
