from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Type, Any

from app.domain.schemas.enums import ResourceType


@dataclass(frozen=True)
class ResourceMeta:
    """
    Immutable configuration for a resource type (Domain View).
    Uses Type[Any] because the Domain doesn't know about SQLModel.
    """
    model: Type[Any]
    event_model: Type[Any]
    fk_field: str


class ResourceRegistry(ABC):
    """
        Abstract Registry Interface.
        Services should depend on this, not the SQL implementation.
    """

    @classmethod
    @abstractmethod
    def get(cls, resource_type: ResourceType) -> ResourceMeta:
        pass
