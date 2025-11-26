from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

from app.domain.schemas.enums import Sites

if TYPE_CHECKING:
    from app.db.sql.models.black import Black
    from app.db.sql.models.mission import Mission


class Station(SQLModel, table=True):
    __tablename__ = 'stations'

    num: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    site: Sites = Field(nullable=False)
    black_num: Optional[int] = Field(
        default=None,
        foreign_key="blacks.num",
        nullable=False,
        ondelete="CASCADE"
    )

    # Relationships
    black: Optional["Black"] = Relationship(
        back_populates="station",
        sa_relationship_kwargs={"lazy": "selectin"}
    )
    missions: List["MissionStation"] = Relationship(
        back_populates="station",
        sa_relationship_kwargs={"cascade": "all, delete"}
    )


class MissionStation(SQLModel, table=True):
    __tablename__ = 'mission_stations'

    id: Optional[int] = Field(default=None, primary_key=True)
    mission_id: int = Field(foreign_key="missions.id", ondelete="CASCADE", index=True)
    station_id: int = Field(foreign_key="stations.num", ondelete="CASCADE", index=True)
    start_time: datetime = Field(index=True, nullable=False)
    end_time: Optional[datetime] = Field(default=None, nullable=True)

    # Relationships
    mission: "Mission" = Relationship(back_populates="mission_stations")
    station: "Station" = Relationship(
        back_populates="missions",
        sa_relationship_kwargs={"lazy": "selectin"}
    )
