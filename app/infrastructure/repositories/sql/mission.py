from datetime import datetime
from typing import List, Any

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, col, or_, delete

from app.db.sql.models.mission import Mission
from app.domain.exceptions.domain_exception import (
    RepositoryException,
    IntegrityViolationException,
    DomainException

)
from app.domain.interfaces.repository import IMissionRepository
from app.domain.schemas.enums import ResourceType
from app.infrastructure.repositories.sql.base import SQLAlchemyRepository
from app.infrastructure.resource_registry.sql.resource_registry import SQLResourceRegistry


class SQLMissionRepository(SQLAlchemyRepository[Mission], IMissionRepository[Mission]):

    def __init__(self, session: AsyncSession):
        super().__init__(session, Mission)

    async def get_mission_full_timeline(self, mission_id: int) -> Mission | None:
        try:
            return await self.get(mission_id)
        except RepositoryException:
            raise
        except Exception as e:
            raise RepositoryException(f"Unexpected error fetching mission {mission_id}") from e

    async def check_resource_availability(
            self,
            resource_type: ResourceType,
            resource_id: int,
            start: datetime,
            end: datetime,
            exclude_mission_id: int | None = None
    ) -> List[Any]:

        try:
            meta = SQLResourceRegistry.get(resource_type)
            event_model = meta.event_model

            # 2. Build Query
            query = select(event_model).where(
                getattr(event_model, meta.fk_field) == resource_id,
                col(event_model.start_time) < end,
                or_(
                    col(event_model.end_time) > start,
                    col(event_model.end_time).is_(None)
                )
            )

            if exclude_mission_id:
                query = query.where(event_model.mission_id != exclude_mission_id)

            result = await self.session.execute(query)
            return [t for t in result.scalars().all()]

        except ValueError as e:
            raise DomainException(f"Configuration error: {str(e)}")
        except SQLAlchemyError as e:
            raise RepositoryException(f"Database error checking availability for {resource_type}") from e

    async def bulk_update_timeline(
            self,
            events_to_create: List[Any],
            events_to_update: List[Any],
            events_to_delete_ids: List[int],
            event_model_type: type
    ) -> None:
        """
        Executes a complex batch of operations.
        Critical failure point: Integrity Errors (Overlaps/Foreign Keys).
        """
        try:
            # 1. Delete
            if events_to_delete_ids:
                stmt = delete(event_model_type).where(event_model_type.id.in_(events_to_delete_ids))  # type: ignore
                await self.session.execute(stmt)

            # 2. Update
            for event in events_to_update:
                self.session.add(event)

            # 3. Create
            for event in events_to_create:
                self.session.add(event)

            # 4. Flush to DB (Checks Constraints)
            await self.session.flush()

        except IntegrityError as e:
            raise IntegrityViolationException(
                f"Timeline update failed due to data conflict. "
                f"The resource might be in use or the times overlap."
            ) from e

        except SQLAlchemyError as e:
            raise RepositoryException("Critical error processing timeline batch update") from e
