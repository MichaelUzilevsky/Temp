from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Any, Optional

from app.domain.schemas.enums import ResourceType


class IRepository[T](ABC):

    @property
    @abstractmethod
    def model(self) -> type[T]:
        """Returns the class type of the model managed by this repo."""
        pass

    @abstractmethod
    async def get(self, id: Any) -> T | None:
        pass

    @abstractmethod
    async def get_multi(self, skip: int = 0, limit: int = 100) -> List[T]:
        pass

    @abstractmethod
    async def create(self, obj_in: T) -> T:
        pass

    @abstractmethod
    async def update(self, obj_current: T, obj_in: Any) -> T:
        pass

    @abstractmethod
    async def delete(self, id: Any) -> bool:
        pass


class IEventRepository(ABC):
    """
    Interface for managing granular timeline events.
    """

    @abstractmethod
    async def get_last_active_event(
            self,
            mission_id: int,
            resource_type: ResourceType
    ) -> Optional[Any]:
        """
        Retrieves the currently open event (end_time is None) for the specific resource type.
        """
        pass

    @abstractmethod
    async def create(self, resource_type: ResourceType, event_obj: Any) -> Any:
        pass

    @abstractmethod
    async def update(self, resource_type: ResourceType, event_obj: Any, update_data: dict) -> Any:
        pass

    @abstractmethod
    async def delete(self, resource_type: ResourceType, event_id: int) -> bool:
        pass

    @abstractmethod
    async def get_by_id(
            self,
            resource_type: ResourceType,
            event_id: int
    ) -> Optional[Any]:
        pass


class IMissionRepository[T](IRepository[T], ABC):
    @abstractmethod
    async def get_mission_full_timeline(self, mission_id: int) -> T | None:
        pass

    @abstractmethod
    async def check_resource_availability(
            self,
            resource_type: ResourceType,
            resource_id: int,
            start: datetime,
            end: datetime,
            exclude_mission_id: int | None = None
    ) -> List[Any]:
        pass

    @abstractmethod
    async def bulk_update_timeline(
            self,
            events_to_create: List[Any],
            events_to_update: List[Any],
            events_to_delete_ids: List[int],
            event_model_type: type
    ) -> None:
        pass


class IOperatorRepository[T](IRepository[T], ABC):
    pass
