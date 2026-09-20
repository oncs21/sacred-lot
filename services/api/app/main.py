from fastapi import FastAPI

from app.core.exceptions import (
    APIException,
    api_exception_handler,
    unexpected_exception_handler,
)
from app.routers import search

app = FastAPI()
app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(Exception, unexpected_exception_handler)
app.include_router(search.router)
