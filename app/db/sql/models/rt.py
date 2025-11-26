from typing import List, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

from app.domain.schemas.enums import RtLocations

if TYPE_CHECKING:
    from app.db.sql.models.platform import MissionPlatform, MissionPlatformRt


class Rt(SQLModel, table=True):
    __tablename__ = 'rts'

    num: int = Field(primary_key=True)  # Assuming config constraints are handled in validation
    location: RtLocations = Field(nullable=False)
    is_main: bool = Field(nullable=False)

    # Relationships
    planned_main_rt_mission_platforms: List["MissionPlatform"] = Relationship(
        back_populates="planned_main_rt",
        sa_relationship_kwargs={
            "foreign_keys": "[MissionPlatform.main_rt_num]"
        }
    )
    planned_backup_rt_mission_platforms: List["MissionPlatform"] = Relationship(
        back_populates="planned_backup_rt",
        sa_relationship_kwargs={
            "foreign_keys": "[MissionPlatform.backup_rt_num]"
        }
    )
    mission_rts: List["MissionPlatformRt"] = Relationship(
        back_populates="linked_rt",
        sa_relationship_kwargs={"cascade": "all, delete"}
    )
