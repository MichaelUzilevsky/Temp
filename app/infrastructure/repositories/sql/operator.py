from typing import Any

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db.sql.models.operator import Operator
from app.db.sql.models.role import Role
from app.domain.exceptions.domain_exception import NotFoundException, IntegrityViolationException, RepositoryException
from app.domain.interfaces.repository import IOperatorRepository
from app.domain.schemas.resources import OperatorCreate, OperatorUpdate
from app.infrastructure.repositories.sql.base import SQLAlchemyRepository


class SQLOperatorRepository(SQLAlchemyRepository[Operator], IOperatorRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Operator)

    async def create(self, obj_in: OperatorCreate) -> Operator:
        try:
            # 1. Create the Operator instance (excluding role_ids)
            db_obj = Operator(**obj_in.model_dump(exclude={"role_ids"}))

            # 2. Handle Many-to-Many Linking
            if obj_in.role_ids:
                # Fetch the actual Role objects from the DB
                stmt = select(Role).where(Role.id.in_(obj_in.role_ids))  # type: ignore
                result = await self.session.execute(stmt)
                roles = result.scalars().all()

                if len(roles) != len(obj_in.role_ids):
                    raise NotFoundException("One or more Role IDs not found")

                db_obj.roles = list(roles)

            self.session.add(db_obj)
            await self.session.flush()
            await self.session.refresh(db_obj)
            return db_obj

        except NotFoundException:
            raise
        except IntegrityError as e:
            raise IntegrityViolationException(
                f"Could not create Operator: Duplicate entry or invalid reference."
            ) from e
        except SQLAlchemyError as e:
            raise RepositoryException("Database error creating Operator") from e

    async def update(self, obj_current: Operator, obj_in: OperatorUpdate | Any) -> Operator:
        try:
            update_data = obj_in.model_dump(exclude_unset=True, exclude={"role_ids"})

            for field, value in update_data.items():
                setattr(obj_current, field, value)

            # Handle Role List updates
            if isinstance(obj_in, OperatorUpdate) and obj_in.role_ids is not None:
                # Fetch new list of roles
                stmt = select(Role).where(Role.id.in_(obj_in.role_ids))  # type: ignore
                result = await self.session.execute(stmt)
                roles = result.scalars().all()

                if len(roles) != len(obj_in.role_ids):
                    raise NotFoundException("One or more Role IDs not found")

                # Replacing the list handles deletions/insertions automatically
                obj_current.roles = list(roles)

            self.session.add(obj_current)
            await self.session.flush()
            await self.session.refresh(obj_current)
            return obj_current

        except NotFoundException:
            raise
        except IntegrityError as e:
            raise IntegrityViolationException("Could not update Operator: Conflict detected.") from e
        except SQLAlchemyError as e:
            raise RepositoryException("Database error updating Operator") from e
