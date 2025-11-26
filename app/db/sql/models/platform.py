from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

from app.domain.schemas.enums import PlatformTypes

if TYPE_CHECKING:
    from app.db.sql.models.mission import Mission
    from app.db.sql.models.rt import Rt


class Platform(SQLModel, table=True):
    __tablename__ = 'platforms'

    tail_num: int = Field(primary_key=True, ge=100, le=999)
    type: PlatformTypes = Field(nullable=False)

    # Relationships
    missions: List["MissionPlatform"] = Relationship(back_populates="platform")
    mission_platforms_rts: List["MissionPlatformRt"] = Relationship(back_populates="platform")


class MissionPlatform(SQLModel, table=True):
    __tablename__ = 'mission_platforms'

    id: Optional[int] = Field(default=None, primary_key=True)
    mission_id: int = Field(foreign_key="missions.id", ondelete="CASCADE", index=True)
    platform_id: int = Field(foreign_key="platforms.tail_num", ondelete="CASCADE", index=True)
    start_time: Optional[datetime] = Field(default=None, nullable=False, index=True)
    end_time: Optional[datetime] = Field(default=None, nullable=True)

    main_rt_num: Optional[int] = Field(default=None, foreign_key="rts.num", ondelete="CASCADE")
    backup_rt_num: Optional[int] = Field(default=None, foreign_key="rts.num", ondelete="CASCADE")

    pod_num: Optional[int] = Field(default=None)
    rass_num: Optional[int] = Field(default=None)
    atru_num: Optional[int] = Field(default=None)

    # Relationships
    mission: "Mission" = Relationship(back_populates="mission_platforms")
    platform: "Platform" = Relationship(
        back_populates="missions",
        sa_relationship_kwargs={"lazy": "selectin"}
    )

    planned_main_rt: Optional["Rt"] = Relationship(
        back_populates="planned_main_rt_mission_platforms",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "foreign_keys": "[MissionPlatform.main_rt_num]"
        }
    )
    planned_backup_rt: Optional["Rt"] = Relationship(
        back_populates="planned_backup_rt_mission_platforms",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "foreign_keys": "[MissionPlatform.backup_rt_num]"
        }
    )


class MissionPlatformRt(SQLModel, table=True):
    __tablename__ = 'mission_platform_rts'

    id: Optional[int] = Field(default=None, primary_key=True)
    mission_id: int = Field(foreign_key="missions.id", ondelete="CASCADE", index=True)
    platform_id: int = Field(foreign_key="platforms.tail_num", ondelete="CASCADE", index=True)
    rt_num: int = Field(foreign_key="rts.num", ondelete="CASCADE", index=True)

    start_time: Optional[datetime] = Field(default=None, nullable=False, index=True)
    end_time: Optional[datetime] = Field(default=None, nullable=True)

    is_active: bool = Field(default=False)
    up_channel: int = Field(default=None, nullable=False)  # Regex logic handled in schema validation
    down_channel: int = Field(default=None, nullable=False)

    # Relationships
    mission: "Mission" = Relationship(back_populates="links")
    platform: "Platform" = Relationship(
        back_populates="mission_platforms_rts",
        sa_relationship_kwargs={"lazy": "selectin"}
    )
    linked_rt: "Rt" = Relationship(
        back_populates="mission_rts",
        sa_relationship_kwargs={"lazy": "selectin"}
    )
