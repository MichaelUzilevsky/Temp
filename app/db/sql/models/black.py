from typing import Optional, List, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

from app.domain.schemas.enums import Sites

if TYPE_CHECKING:
    from app.db.sql.models.station import Station
    from app.db.sql.models.crawler import Crawler


class Black(SQLModel, table=True):
    __tablename__ = 'blacks'

    num: Optional[int] = Field(default=None, primary_key=True, index=True)
    name: str = Field(unique=True, nullable=False)
    site: Sites = Field(nullable=False)

    # Relationships
    station: Optional["Station"] = Relationship(
        back_populates="black",
        sa_relationship_kwargs={"cascade": "all, delete"}
    )
    crawlers: List["Crawler"] = Relationship(
        back_populates="black",
        sa_relationship_kwargs={"cascade": "all, delete"}
    )
