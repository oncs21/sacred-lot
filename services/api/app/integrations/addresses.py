import sqlite3
from contextlib import closing

from starlette.concurrency import run_in_threadpool

from app.core.address_search import search
from app.core.config import get_settings
from app.core.exceptions import APIException
from app.schemas.address import AddressSuggestion


def _lookup(address: str, limit: int) -> list[AddressSuggestion]:
    settings = get_settings()
    uri = settings.address_database.expanduser().resolve().as_uri() + "?mode=ro"
    try:
        with closing(sqlite3.connect(uri, uri=True, timeout=2.0)) as connection:
            version = connection.execute(
                "SELECT value FROM metadata WHERE key = 'schema_version'"
            ).fetchone()
            if version != ("1",):
                raise ValueError("Unsupported address database version")
            return [
                AddressSuggestion(address=row[0], latitude=row[1], longitude=row[2])
                for row in search(connection, address, limit, settings.geocoding_bbox)
            ]
    except (sqlite3.Error, OSError, ValueError) as exc:
        raise APIException(
            status_code=503,
            error_code="ADDRESS_DATABASE_UNAVAILABLE",
            message="The local address database is unavailable or incompatible.",
            user_message="Address suggestions are temporarily unavailable. Please try again later.",
        ) from exc


async def fetch_address_suggestions(
    address: str, limit: int = 5
) -> list[AddressSuggestion]:
    return await run_in_threadpool(_lookup, address, limit)
