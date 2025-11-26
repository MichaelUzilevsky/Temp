from fastapi import APIRouter, Depends, status

from app.api.dependencies.service import get_mission_service
from app.api.factories.mission_router_factory import register_mission_resource_routes
from app.application.services.mission_service import MissionService
from app.domain.schemas import events as event_schemas
from app.domain.schemas import mission as mission_schemas
from app.domain.schemas.enums import ResourceType

router = APIRouter(prefix="/missions", tags=["Missions"])


@router.post("", response_model=mission_schemas.MissionRead, status_code=status.HTTP_201_CREATED)
async def create_mission(
        payload: mission_schemas.MissionCreate,
        service: MissionService = Depends(get_mission_service)
):
    return await service.create(payload)


@router.get("/{id}", response_model=mission_schemas.MissionRead)
async def get_mission(
        id: int,
        service: MissionService = Depends(get_mission_service)
):
    return await service.get_full_timeline(id)


resources_config = [
    (
        ResourceType.STATION, "stations",
        event_schemas.BatchStationUpdate,
        event_schemas.MissionStationCreate,
        event_schemas.MissionStationUpdate
    ),
    (
        ResourceType.CRAWLER, "crawlers",
        event_schemas.BatchCrawlerUpdate,
        event_schemas.MissionCrawlerCreate,
        event_schemas.MissionCrawlerUpdate
    ),
    (
        ResourceType.PLATFORM, "platforms",
        event_schemas.BatchPlatformUpdate,
        event_schemas.MissionPlatformCreate,
        event_schemas.MissionPlatformUpdate
    ),
    (
        ResourceType.RT, "rts",
        event_schemas.BatchRtUpdate,
        event_schemas.MissionPlatformRtCreate,
        event_schemas.MissionPlatformRtUpdate
    ),
    (
        ResourceType.OPERATOR, "operators",
        event_schemas.BatchOperatorUpdate,
        event_schemas.MissionOperatorCreate,
        event_schemas.MissionOperatorUpdate
    )
]

for res_type, slug, batch, create, update in resources_config:
    register_mission_resource_routes(
        router=router,
        resource_type=res_type,
        slug=slug,
        batch_schema=batch,
        create_schema=create,
        update_schema=update
    )
