from typing import Type, List, Any

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from app.api.dependencies.service import get_generic_service_factory
from app.application.services.base_service import BaseService


def create_crud_router(
        model_class: Any,  # SQLModel class
        read_schema: Type[BaseModel],
        create_schema: Type[BaseModel],
        update_schema: Type[BaseModel],
        prefix: str,
        tags: List[str]
) -> APIRouter:
    """
    Generates a standard CRUD router for a resource.
    """
    router = APIRouter(prefix=prefix, tags=tags)

    # Create the dependency specifically for this model
    get_service = get_generic_service_factory(model_class)

    @router.get("/{id}", response_model=read_schema)
    async def get_one(
            id: int,
            service: BaseService = Depends(get_service)
    ):
        return await service.get(id)

    @router.get("", response_model=List[read_schema])
    async def get_multi(
            skip: int = 0,
            limit: int = 100,
            service: BaseService = Depends(get_service)
    ):
        return await service.get_multi(skip, limit)

    @router.post("", response_model=read_schema, status_code=status.HTTP_201_CREATED)
    async def create(
            payload: create_schema,
            service: BaseService = Depends(get_service)
    ):
        return await service.create(payload)

    @router.patch("/{id}", response_model=read_schema)
    async def update(
            id: int,
            payload: update_schema,
            service: BaseService = Depends(get_service)
    ):
        return await service.update(id, payload)

    @router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete(
            id: int,
            service: BaseService = Depends(get_service)
    ):
        await service.delete(id)
        return

    return router
