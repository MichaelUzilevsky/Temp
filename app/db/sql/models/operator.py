from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.db.sql.models.role import Role
    from app.db.sql.models.mission import Mission


class Operator(SQLModel, table=True):
    __tablename__ = 'operators'

    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str = Field(nullable=False)
    last_name: str = Field(nullable=False)

    # Relationships
    roles: List["OperatorRole"] = Relationship(
        back_populates="operator",
        sa_relationship_kwargs={"lazy": "selectin"}
    )
    missions: List["MissionOperators"] = Relationship(
        back_populates="operator",
        sa_relationship_kwargs={"cascade": "all, delete"}
    )


class OperatorRole(SQLModel, table=True):
    __tablename__ = 'operator_roles'

    id: Optional[int] = Field(default=None, primary_key=True)
    operator_id: int = Field(foreign_key="operators.id", ondelete="CASCADE", index=True)
    role_id: int = Field(foreign_key="roles.id", ondelete="CASCADE", index=True)

    # Relationships
    operator: "Operator" = Relationship(
        back_populates="roles",
        sa_relationship_kwargs={"lazy": "selectin"}
    )
    role: "Role" = Relationship(
        back_populates="operators",
        sa_relationship_kwargs={"lazy": "selectin"}
    )


class MissionOperators(SQLModel, table=True):
    __tablename__ = 'mission_operators'

    id: Optional[int] = Field(default=None, primary_key=True)
    mission_id: int = Field(foreign_key="missions.id", ondelete="CASCADE", index=True)
    operator_id: int = Field(foreign_key="operators.id", ondelete="CASCADE", index=True)
    role_id: int = Field(foreign_key="roles.id", ondelete="CASCADE", index=True)

    start_time: Optional[datetime] = Field(index=True, nullable=False)
    end_time: Optional[datetime] = Field(default=None, nullable=True)

    # Relationships
    mission: "Mission" = Relationship(back_populates="mission_operators")
    operator: "Operator" = Relationship(
        back_populates="missions",
        sa_relationship_kwargs={"lazy": "selectin"}
    )
    role: "Role" = Relationship(
        back_populates="mission_roles",
        sa_relationship_kwargs={"lazy": "selectin"}
    )
