from datetime import datetime, timezone
from typing import Any, Dict, Type

from pydantic import BaseModel

from app.domain.exceptions.domain_exception import NotFoundException, ResourceUnavailableException
from app.domain.interfaces.repository import IEventRepository
from app.domain.interfaces.repository import IMissionRepository
from app.domain.interfaces.resource_registry import ResourceRegistry
from app.domain.schemas.enums import ResourceType


class MissionEventService:
    """
    Handles granular operations on Mission Events (Real-Time Switching & CRUD).
    """

    def __init__(
            self,
            mission_repository: IMissionRepository,
            event_repository: IEventRepository,
            resource_registry: Type[ResourceRegistry]
    ):
        self.mission_repo = mission_repository
        self.event_repo = event_repository
        self.resource_registry = resource_registry

    async def switch_resource(
            self,
            mission_id: int,
            resource_type: ResourceType,
            event_data: BaseModel
    ) -> Any:
        """
        Real-Time Operation: Atomic Switch.
        1. Idempotency Check (Don't switch if already active).
        2. Closes the currently active event.
        3. Opens a new event.
        """
        # 1. Use UTC for all logic
        now = datetime.now(timezone.utc)
        meta = self.resource_registry.get(resource_type)

        # 2. Extract Resource ID
        new_resource_id = getattr(event_data, meta.fk_field, None)
        if new_resource_id is None:
            raise ValueError(f"Input data missing required field: {meta.fk_field}")

        # 3. Get Current Active Event
        active_event = await self.event_repo.get_last_active_event(mission_id, resource_type)

        # 4. Idempotency Check (Production Safeguard)
        # If the mission is ALREADY using this resource, do nothing.
        if active_event:
            current_resource_id = getattr(active_event, meta.fk_field)
            if current_resource_id == new_resource_id:
                return active_event

        # 5. Availability Check
        # Ensure max time is UTC aware to match 'now'
        max_time = datetime.max.replace(tzinfo=timezone.utc)
        conflicts = await self.mission_repo.check_resource_availability(
            resource_type=resource_type,
            resource_id=new_resource_id,
            start=now,
            end=max_time,
            exclude_mission_id=mission_id
        )
        if conflicts:
            raise ResourceUnavailableException(f"Resource {new_resource_id} is currently in use.")

        # 6. Close old event
        if active_event:
            # We assume update takes a dict for partial updates
            await self.event_repo.update(resource_type, active_event, {"end_time": now})

        # 7. Create new event
        data_dict = event_data.model_dump()
        data_dict["mission_id"] = mission_id
        data_dict["start_time"] = now
        data_dict["end_time"] = None

        new_event_obj = meta.event_model(**data_dict)
        return await self.event_repo.create(resource_type, new_event_obj)

    async def create_event(
            self,
            mission_id: int,
            resource_type: ResourceType,
            event_data: BaseModel
    ) -> Any:
        """
        Manually adds a historical or future event using full model data.
        """
        meta = self.resource_registry.get(resource_type)

        # 1. Validation
        new_resource_id = getattr(event_data, meta.fk_field, None)
        start_time = getattr(event_data, "start_time")
        end_time = getattr(event_data, "end_time", None)

        # Ensure max time is UTC aware
        max_time = datetime.max.replace(tzinfo=timezone.utc)
        conflicts = await self.mission_repo.check_resource_availability(
            resource_type=resource_type,
            resource_id=new_resource_id,
            start=start_time,
            end=end_time or max_time,
            exclude_mission_id=mission_id
        )
        if conflicts:
            raise ResourceUnavailableException(f"Resource {new_resource_id} is busy during the requested time.")

        # 2. Create
        data_dict = event_data.model_dump()
        data_dict["mission_id"] = mission_id

        new_event_obj = meta.event_model(**data_dict)
        return await self.event_repo.create(resource_type, new_event_obj)

    async def update_event(
            self,
            resource_type: ResourceType,
            event_id: int,
            update_data: Dict[str, Any]
    ) -> Any:
        """
        Updates a specific event by ID.
        """
        # 1. Get existing
        event = await self.event_repo.get_by_id(resource_type, event_id)
        if not event:
            raise NotFoundException(f"Event {event_id} not found")

        # 2. Update
        return await self.event_repo.update(resource_type, event, update_data)

    async def delete_event(
            self,
            resource_type: ResourceType,
            event_id: int
    ) -> bool:
        """
        Deletes a specific event by ID.
        """
        success = await self.event_repo.delete(resource_type, event_id)
        if not success:
            raise NotFoundException(f"Event {event_id} not found")
        return True
