from typing import Type

from fastapi import Depends

from app.api.dependencies.db import get_db_manager
from app.db.sql.manager import SQLAlchemyManager
from app.domain.interfaces.resource_registry import ResourceRegistry
from app.infrastructure.resource_registry.sql.resource_registry import SQLResourceRegistry


def get_resource_registry(
        db_manager=Depends(get_db_manager),
) -> Type[ResourceRegistry]:
    if isinstance(db_manager, SQLAlchemyManager):
        return SQLResourceRegistry
    else:
        raise RuntimeError("Unknown DB manager")
