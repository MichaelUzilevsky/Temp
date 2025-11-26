from app.db.sql.models.operator import Operator

from app.application.services.base_service import BaseService
from app.domain.schemas.resources import OperatorCreate, OperatorUpdate
from app.infrastructure.repositories.sql.operator import SQLOperatorRepository


class OperatorService(BaseService[Operator, OperatorCreate, OperatorUpdate]):
    """
    Service for managing Operators.

    Why is this needed?
    Because 'OperatorCreate' contains 'role_ids' (List[int]), but the 'Operator'
    DB model expects 'roles' (List[Role]).

    The BaseService logic would try to do Operator(**role_ids=[...]) which would fail.
    The SQLOperatorRepository overrides create/update to handle this logic,
    so we just need to type-hint the repository correctly here.
    """

    def __init__(self, repository: SQLOperatorRepository):
        super().__init__(repository)
        self.repository = repository
