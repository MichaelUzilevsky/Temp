from typing import Any, Optional, Type

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, SQLModel

from app.domain.interfaces.repository import IEventRepository
from app.domain.schemas.enums import ResourceType
from app.infrastructure.repositories.sql.base import SQLAlchemyRepository
from app.infrastructure.resource_registry.sql.resource_registry import SQLResourceRegistry


class SQLEventRepository(IEventRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _get_repo_for_type(self, resource_type: ResourceType) -> SQLAlchemyRepository:
        """
        Helper: Creates a temporary generic repository configured for the specific resource type.
        This allows us to reuse all the robust error handling and CRUD logic from the base class.
        """
        meta = SQLResourceRegistry.get(resource_type)
        return SQLAlchemyRepository(self.session, meta.event_model)

    async def get_last_active_event(self, mission_id: int, resource_type: ResourceType) -> Optional[Any]:
        meta = SQLResourceRegistry.get(resource_type)
        event_model: Type[SQLModel] = meta.event_model

        # We look for the event that has NO end_time (is currently active)
        statement = select(event_model).where(
            event_model.mission_id == mission_id,
            event_model.end_time.is_(None)
        )
        # If there are multiple, we take the latest start_time
        statement = statement.order_by(event_model.start_time.desc()).limit(1)

        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_id(self, resource_type: ResourceType, event_id: int) -> Optional[Any]:
        # meta = SQLResourceRegistry.get(resource_type)
        # event_model = meta.event_model
        # return await self.session.get(event_model, event_id)

        # Delegate to generic repo
        return await self._get_repo_for_type(resource_type).get(event_id)

    async def create(self, resource_type: ResourceType, event_obj: Any) -> Any:
        # self.session.add(event_obj)
        # await self.session.flush()
        # await self.session.refresh(event_obj)
        # return event_obj

        # Delegate to generic repo (Handles Flush, Refresh, IntegrityErrors)
        return await self._get_repo_for_type(resource_type).create(event_obj)

    async def update(self, resource_type: ResourceType, event_obj: Any, update_data: dict) -> Any:
        # for key, value in update_data.items():
        #     setattr(event_obj, key, value)
        #
        # self.session.add(event_obj)
        # await self.session.flush()
        # await self.session.refresh(event_obj)
        # return event_obj

        # Delegate to generic repo
        return await self._get_repo_for_type(resource_type).update(event_obj, update_data)

    async def delete(self, resource_type: ResourceType, event_id: int) -> bool:
        # event = await self.get_by_id(resource_type, event_id)
        # if event:
        #     await self.session.delete(event)
        #     await self.session.flush()
        #     return True
        # return False

        # Delegate to generic repo
        return await self._get_repo_for_type(resource_type).delete(event_id)
