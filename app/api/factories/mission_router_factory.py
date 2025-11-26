from typing import Type

from fastapi import APIRouter, Depends, status, Path
from pydantic import BaseModel

from app.api.dependencies.service import get_mission_service, get_mission_event_service
from app.application.services.mission_event_service import MissionEventService
from app.application.services.mission_service import MissionService
from app.domain.schemas.enums import ResourceType


def register_mission_resource_routes(
        router: APIRouter,
        resource_type: ResourceType,
        slug: str,
        batch_schema: Type[BaseModel],
        create_schema: Type[BaseModel],
        update_schema: Type[BaseModel]
):
    """
    Dynamically registers Batch, Switch, and Granular CRUD endpoints for a resource type
    onto the provided router.
    """

    # --- A. Batch Timeline Update ---
    @router.patch(f"/{{id}}/timeline/{slug}", status_code=status.HTTP_204_NO_CONTENT)
    async def update_timeline_batch(
            payload: batch_schema,
            id: int = Path(..., description="Mission ID"),
            service: MissionService = Depends(get_mission_service)
    ):
        payload.mission_id = id
        await service.update_timeline(
            mission_id=id,
            resource_type=resource_type,
            creates=payload.creates,
            updates=payload.updates,
            deletes=payload.deletes,
            auto_fix=payload.auto_fix_gaps
        )

    # --- B. Real-Time Switch ---
    @router.post(f"/{{id}}/{slug}/switch", status_code=status.HTTP_200_OK)
    async def switch_resource(
            payload: create_schema,
            id: int = Path(..., description="Mission ID"),
            service: MissionEventService = Depends(get_mission_event_service)
    ):
        return await service.switch_resource(
            mission_id=id,
            resource_type=resource_type,
            event_data=payload
        )

    # 1. Create specific event
    @router.post(f"/{{id}}/{slug}", status_code=status.HTTP_201_CREATED)
    async def create_event(
            payload: create_schema,
            id: int = Path(..., description="Mission ID"),
            service: MissionEventService = Depends(get_mission_event_service)
    ):
        return await service.create_event(id, resource_type, payload)

    # 2. Update specific event
    @router.patch(f"/{{id}}/{slug}/{{event_id}}", status_code=status.HTTP_200_OK)
    async def update_event(
            payload: update_schema,
            id: int = Path(..., description="Mission ID"),  # Accepted for URL consistency
            event_id: int = Path(..., description="Event ID to update"),
            service: MissionEventService = Depends(get_mission_event_service)
    ):
        payload.id = event_id
        update_data = payload.model_dump(exclude_unset=True)

        return await service.update_event(resource_type, event_id, update_data)

    # 3. Delete specific event
    @router.delete(f"/{{id}}/{slug}/{{event_id}}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_event(
            id: int = Path(..., description="Mission ID"),  # Accepted for URL consistency
            event_id: int = Path(..., description="Event ID to delete"),
            service: MissionEventService = Depends(get_mission_event_service)
    ):
        await service.delete_event(resource_type, event_id)
