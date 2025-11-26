from typing import Optional, List, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

from app.domain.schemas.enums import OperatorRolesEnum

if TYPE_CHECKING:
    from app.db.sql.models.operator import OperatorRole, MissionOperators


class Role(SQLModel, table=True):
    __tablename__ = 'roles'

    id: Optional[int] = Field(default=None, primary_key=True)
    name: OperatorRolesEnum = Field(nullable=False)

    # Relationships
    operators: List["OperatorRole"] = Relationship(
        back_populates="role",
        sa_relationship_kwargs={"cascade": "all, delete"}
    )
    mission_roles: List["MissionOperators"] = Relationship(
        back_populates="role",
        sa_relationship_kwargs={"cascade": "all, delete"}
    )
