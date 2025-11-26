from typing import Any, List

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, SQLModel

from app.domain.exceptions.domain_exception import (
    IntegrityViolationException,
    RepositoryException
)
from app.domain.interfaces.repository import IRepository


class SQLAlchemyRepository[T: SQLModel](IRepository[T]):

    def __init__(self, session: AsyncSession, model: type[T]):
        self.session = session
        self._model = model

    @property
    def model(self) -> type[T]:
        return self._model

    @model.setter
    def model(self, value):
        self._model = value

    async def get(self, id: Any) -> T | None:
        try:
            statement = select(self.model).where(self.model.id == id)
            result = await self.session.execute(statement)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise RepositoryException(f"Database error retrieving {self.model.__name__}") from e

    async def get_multi(self, skip: int = 0, limit: int = 100) -> List[T]:
        try:
            statement = select(self.model).offset(skip).limit(limit)
            result = await self.session.execute(statement)
            return [t for t in result.scalars().all()]
        except SQLAlchemyError as e:
            raise RepositoryException(f"Database error retrieving list of {self.model.__name__}") from e

    async def create(self, obj_in: T) -> T:
        try:
            self.session.add(obj_in)
            await self.session.flush()  # This is where constraints are checked
            await self.session.refresh(obj_in)
            return obj_in
        except IntegrityError as e:
            # TODO: Change this to a unique exception based on the error
            raise IntegrityViolationException(
                f"Could not create {self.model.__name__}: Duplicate entry or invalid reference.") from e
        except SQLAlchemyError as e:
            raise RepositoryException(f"Database error creating {self.model.__name__}") from e

    async def update(self, obj_current: T, obj_in: Any) -> T:
        try:
            if hasattr(obj_in, "model_dump"):
                update_data = obj_in.model_dump(exclude_unset=True)
            elif isinstance(obj_in, dict):
                update_data = obj_in
            else:
                update_data = {}

            for field, value in update_data.items():
                setattr(obj_current, field, value)

            self.session.add(obj_current)
            await self.session.flush()
            await self.session.refresh(obj_current)
            return obj_current
        except IntegrityError as e:
            raise IntegrityViolationException(f"Could not update {self.model.__name__}: Conflict detected.") from e
        except SQLAlchemyError as e:
            raise RepositoryException(f"Database error updating {self.model.__name__}") from e

    async def delete(self, id: Any) -> bool:
        try:
            obj = await self.get(id)
            if obj:
                await self.session.delete(obj)
                await self.session.flush()
                return True
            return False
        except IntegrityError as e:
            raise IntegrityViolationException(
                f"Cannot delete {self.model.__name__}: It is being used by another resource.") from e
        except SQLAlchemyError as e:
            raise RepositoryException(f"Database error deleting {self.model.__name__}") from e
