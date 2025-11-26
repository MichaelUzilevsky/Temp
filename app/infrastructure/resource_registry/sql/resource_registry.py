from dataclasses import dataclass
from typing import Type

from sqlmodel import SQLModel

from app.db.sql.models.crawler import Crawler, MissionCrawler
from app.db.sql.models.operator import Operator, MissionOperators
from app.db.sql.models.platform import Platform, MissionPlatform, MissionPlatformRt
from app.db.sql.models.rt import Rt
from app.db.sql.models.station import Station, MissionStation
from app.domain.interfaces.resource_registry import ResourceMeta, ResourceRegistry
from app.domain.schemas.enums import ResourceType


@dataclass(frozen=True)
class SQLResourceMeta(ResourceMeta):
    """
    SQL-specific configuration refining the types.
    This allows Infrastructure code to know these are definitely SQLModels.
    """
    model: Type[SQLModel]
    event_model: Type[SQLModel]


class SQLResourceRegistry(ResourceRegistry):
    """
    Centralized registry mapping Domain Enums to Infrastructure Models.
    """
    _registry: dict[ResourceType, SQLResourceMeta] = {
        ResourceType.STATION: SQLResourceMeta(
            model=Station,
            event_model=MissionStation,
            fk_field="station_id"
        ),
        ResourceType.CRAWLER: SQLResourceMeta(
            model=Crawler,
            event_model=MissionCrawler,
            fk_field="crawler_id"
        ),
        ResourceType.PLATFORM: SQLResourceMeta(
            model=Platform,
            event_model=MissionPlatform,
            fk_field="platform_id"
        ),
        ResourceType.RT: SQLResourceMeta(
            model=Rt,
            event_model=MissionPlatformRt,
            fk_field="rt_num"
        ),
        ResourceType.OPERATOR: SQLResourceMeta(
            model=Operator,
            event_model=MissionOperators,
            fk_field="operator_id"
        )
    }

    @classmethod
    def get(cls, resource_type: ResourceType) -> SQLResourceMeta:
        meta = cls._registry.get(resource_type)
        if not meta:
            raise ValueError(f"Resource type '{resource_type}' is not registered in ResourceRegistry.")
        return meta
