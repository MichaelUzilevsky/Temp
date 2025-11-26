from fastapi import Request
from fastapi.responses import JSONResponse

from app.domain.exceptions.domain_exception import DomainException


async def domain_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, DomainException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message}
        )
    # fallback for other exceptions
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"}
    )


# Optional: fallback for unhandled exceptions
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
