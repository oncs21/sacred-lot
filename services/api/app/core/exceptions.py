import logging

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ErrorSchema(BaseModel):
    error_code: str
    message: str
    user_message: str


class APIException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_code: str = "GENERIC_ERROR",
        message: str = "An error occurred while processing the request.",
        user_message: str = "Something went wrong.. Please try again.",
    ):
        super().__init__(
            status_code=status_code,
            detail={
                "error_code": error_code,
                "message": message,
                "user_message": user_message,
            },
        )

        self.error_code = error_code
        self.message = message
        self.user_message = user_message


async def api_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, APIException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    return await unexpected_exception_handler(request, exc)


async def unexpected_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    logger.error(
        "Unhandled API exception", exc_info=(type(exc), exc, exc.__traceback__)
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": {
                "error_code": "INTERNAL_SERVER_ERROR",
                "message": "An internal server error occurred.",
                "user_message": "An unexpected server error occurred.",
            }
        },
    )
