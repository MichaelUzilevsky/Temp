from typing import AsyncGenerator

from app.db.base_manager import AbstractDBManager
from fastapi import Depends, Request


async def get_db_manager(request: Request) -> AbstractDBManager:
    return request.app.state.db_manager


async def get_session(
        db_manager: AbstractDBManager = Depends(get_db_manager)
) -> AsyncGenerator:
    """
    Yields a database session that is automatically committed/rolled back
    by the context manager in db_manager.
    """
    async with db_manager.get_connection() as session:
        async with db_manager.transaction(session) as tx_session:
            yield tx_session
