from typing import List

from fastapi import APIRouter, Depends, status

from app.api.dependencies.service import get_operator_service
from app.application.services.operator_service import OperatorService
from app.domain.schemas import resources as schemas

router = APIRouter(prefix="/operators", tags=["Operators"])


@router.post("", response_model=schemas.OperatorRead, status_code=status.HTTP_201_CREATED)
async def create_operator(
        payload: schemas.OperatorCreate,
        service: OperatorService = Depends(get_operator_service)
):
    return await service.create(payload)


@router.get("", response_model=List[schemas.OperatorRead])
async def get_operators(
        skip: int = 0, limit: int = 100,
        service: OperatorService = Depends(get_operator_service)
):
    return await service.get_multi(skip, limit)


@router.get("/{id}", response_model=schemas.OperatorRead)
async def get_operator(
        id: int,
        service: OperatorService = Depends(get_operator_service)
):
    return await service.get(id)


@router.patch("/{id}", response_model=schemas.OperatorRead)
async def update_operator(
        id: int,
        payload: schemas.OperatorUpdate,
        service: OperatorService = Depends(get_operator_service)
):
    return await service.update(id, payload)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_operator(
        id: int,
        service: OperatorService = Depends(get_operator_service)
):
    await service.delete(id)
