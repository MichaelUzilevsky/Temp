from typing import Type

from fastapi import Depends

from app.api.dependencies.db import get_session
from app.api.dependencies.registry import get_resource_registry
from app.api.dependencies.reopository import get_mission_repo, get_event_repo, get_operator_repo, get_generic_repo_class
from app.application.services.base_service import BaseService
from app.application.services.mission_event_service import MissionEventService
from app.application.services.mission_service import MissionService
from app.application.services.operator_service import OperatorService
from app.application.services.timeline_calculator import TimelineCalculator
from app.domain.interfaces.resource_registry import ResourceRegistry
from app.infrastructure.repositories.sql.event_repository import SQLEventRepository
from app.infrastructure.repositories.sql.mission import SQLMissionRepository
from app.infrastructure.repositories.sql.operator import SQLOperatorRepository


def get_timeline_calculator() -> TimelineCalculator:
    return TimelineCalculator()


def get_mission_service(
        repo: SQLMissionRepository = Depends(get_mission_repo),
        calc: TimelineCalculator = Depends(get_timeline_calculator),
        resource_registry: Type[ResourceRegistry] = Depends(get_resource_registry),
) -> MissionService:
    return MissionService(repo, calc, resource_registry)


def get_mission_event_service(
        mission_repo: SQLMissionRepository = Depends(get_mission_repo),
        event_repo: SQLEventRepository = Depends(get_event_repo),
        resource_registry: Type[ResourceRegistry] = Depends(get_resource_registry),
) -> MissionEventService:
    return MissionEventService(mission_repo, event_repo, resource_registry)


def get_operator_service(
        repo: SQLOperatorRepository = Depends(get_operator_repo)
) -> OperatorService:
    return OperatorService(repo)


def get_generic_service_factory[T](model_class: Type[T]):
    """
    Creates a dependency that returns a BaseService for a specific model.
    Decoupled from specific Repo implementation via dependency injection.
    """

    def _get_service(
            session=Depends(get_session),
            repo_class=Depends(get_generic_repo_class)
    ) -> BaseService:
        repo = repo_class(session, model_class)
        return BaseService(repo)

    return _get_service
