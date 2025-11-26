from typing import List, Any

from pydantic import BaseModel

from app.domain.exceptions.domain_exception import NotFoundException
from app.domain.interfaces.repository import IRepository


class BaseService[T, CreateSchema: BaseModel, UpdateSchema: BaseModel]:
    """
    Base Service for standard CRUD operations.
    """

    def __init__(self, repository: IRepository[T]):
        self.repository = repository
        self.model = repository.model

    async def get(self, id: Any) -> T:
        """
        Fetches a resource by ID.
        Exceptions: Bubbles up Repository exceptions; raises NotFoundException if None.
        """
        item = await self.repository.get(id)
        if not item:
            raise NotFoundException(f"Resource with id {id} not found")
        return item

    async def get_multi(self, skip: int = 0, limit: int = 100) -> List[T]:
        """
        Fetches a list of resources.
        """
        return await self.repository.get_multi(skip, limit)

    async def create(self, obj_in: CreateSchema) -> T:
        """
        Creates a new resource.

        Logic:
        1. Converts Pydantic Schema -> Domain/DB Model.
        2. Calls Repository.create().
        """
        # Ensure we have the model class to instantiate
        if not self.model:
            raise NotImplementedError(
                "Service cannot determine Model Class from Repository. "
                "Ensure Repository has 'model' attribute or override create()"
            )

        # Convert Pydantic Schema to SQLModel/DB Entity
        db_obj = self.model.model_validate(obj_in)

        return await self.repository.create(db_obj)

    async def update(self, id: Any, obj_in: UpdateSchema) -> T:
        """
        Updates an existing resource.
        """
        current = await self.get(id)
        # We pass the Pydantic schema directly to the repository's update method.
        # The generic SQLAlchemyRepository knows how to call .model_dump() on it.
        return await self.repository.update(current, obj_in)

    async def delete(self, id: Any) -> bool:
        """
        Deletes a resource.
        """
        await self.get(id)  # Check existence first
        return await self.repository.delete(id)
