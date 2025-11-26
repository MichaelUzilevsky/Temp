from typing import Type

from app.db.sql.manager import SQLAlchemyManager
from fastapi import Depends

from app.api.dependencies.db import get_db_manager, get_session
from app.domain.interfaces.repository import IMissionRepository, IEventRepository, IOperatorRepository, IRepository
from app.infrastructure.repositories.sql.base import SQLAlchemyRepository
from app.infrastructure.repositories.sql.event_repository import SQLEventRepository
from app.infrastructure.repositories.sql.mission import SQLMissionRepository
from app.infrastructure.repositories.sql.operator import SQLOperatorRepository


def get_generic_repo_class(
        db_manager=Depends(get_db_manager)
) -> Type[IRepository]:
    if isinstance(db_manager, SQLAlchemyManager):
        return SQLAlchemyRepository
    else:
        raise RuntimeError("Unknown DB manager")


def get_mission_repo(
        conn=Depends(get_session),
        db_manager=Depends(get_db_manager),
) -> IMissionRepository:
    if isinstance(db_manager, SQLAlchemyManager):
        return SQLMissionRepository(conn)
    else:
        raise RuntimeError("Unknown DB manager")


def get_event_repo(
        conn=Depends(get_session),
        db_manager=Depends(get_db_manager)
) -> IEventRepository:
    if isinstance(db_manager, SQLAlchemyManager):
        return SQLEventRepository(conn)
    else:
        raise RuntimeError("Unknown DB manager")


def get_operator_repo(
        conn=Depends(get_session),
        db_manager=Depends(get_db_manager)
) -> IOperatorRepository:
    if isinstance(db_manager, SQLAlchemyManager):
        return SQLOperatorRepository(conn)
    else:
        raise RuntimeError("Unknown DB manager")
