from datetime import datetime, timezone
from typing import List, Any, Type

from app.application.services.base_service import BaseService
from app.application.services.timeline_calculator import TimelineCalculator
from app.db.sql.models.mission import Mission
from app.domain.exceptions.domain_exception import ResourceUnavailableException, DomainException
from app.domain.interfaces.repository import IMissionRepository
from app.domain.interfaces.resource_registry import ResourceRegistry
from app.domain.schemas.enums import ResourceType
from app.domain.schemas.mission import MissionCreate, MissionUpdate


class MissionService(BaseService[Mission, MissionCreate, MissionUpdate]):
    def __init__(
            self,
            repository: IMissionRepository,
            timeline_calculator: TimelineCalculator,
            resource_registry: Type[ResourceRegistry]
    ):
        super().__init__(repository)
        self.mission_repo = repository
        self.calculator = timeline_calculator
        self.resource_registry = resource_registry

    async def get_full_timeline(self, mission_id: int) -> Mission:
        return await self.get(mission_id)

    async def update_timeline(
            self,
            mission_id: int,
            resource_type: ResourceType,
            creates: List[Any],
            updates: List[Any],
            deletes: List[int],
            auto_fix: bool = True
    ) -> None:
        """
        Handles batch updates for a SPECIFIC resource timeline.
        """
        meta = self.resource_registry.get(resource_type)

        # A. Fetch Current Events for this specific resource type
        mission = await self.get(mission_id)
        attr_name = f"mission_{resource_type.value}s"

        if not hasattr(mission, attr_name):
            raise DomainException(f"Relationship {attr_name} not found on Mission model.")

        current_events = getattr(mission, attr_name, [])

        # B. Availability Checks
        # Only check items that change time or resource ID
        for item in creates + updates:
            res_id = getattr(item, meta.fk_field, None)

            # If update doesn't change resource_id, we might need to fetch the existing event to know the ID
            # But usually, updates just shift time.
            # If creates, we MUST check availability.
            if res_id:
                # Ensure strict timezone handling
                start_time = getattr(item, "start_time")
                end_time = getattr(item, "end_time", None)

                # If end_time is None (active) or not provided, assume max time for the check
                if end_time is None:
                    end_time = datetime.max.replace(tzinfo=timezone.utc)

                conflicts = await self.mission_repo.check_resource_availability(
                    resource_type=resource_type,
                    resource_id=res_id,
                    start=start_time,
                    end=end_time,
                    exclude_mission_id=mission_id
                )
                if conflicts:
                    raise ResourceUnavailableException(f"Resource {res_id} is busy.")

        # C. Calculator
        # Helper to convert Pydantic schema -> SQLModel
        def schema_to_model_factory(schema):
            data = schema.model_dump()
            data["mission_id"] = mission_id
            return meta.event_model(**data)

        change_plan = self.calculator.calculate_changes(
            current_events=list(current_events),
            updates=updates,
            creates=creates,
            deletes=deletes,
            auto_fix=auto_fix,
            model_factory=schema_to_model_factory  # Pass the factory
        )

        # D. Bulk Update
        await self.mission_repo.bulk_update_timeline(
            events_to_create=change_plan.to_create,
            events_to_update=change_plan.to_update,
            events_to_delete_ids=change_plan.to_delete_ids,
            event_model_type=meta.event_model
        )
