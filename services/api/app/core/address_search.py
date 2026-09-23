import re
import sqlite3
import unicodedata

ALIASES: dict[str, str] = {
    "STREET": "ST",
    "AVENUE": "AVE",
    "ROAD": "RD",
    "BOULEVARD": "BLVD",
    "DRIVE": "DR",
    "LANE": "LN",
    "COURT": "CT",
    "NORTH": "N",
    "SOUTH": "S",
    "EAST": "E",
    "WEST": "W",
}


def normalize(value: str) -> str:
    value = (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().upper()
    )
    tokens: list[str] = re.findall(r"[A-Z0-9]+", value)
    normalized_tokens = [ALIASES.get(token, token) for token in tokens]
    return " ".join(normalized_tokens)


def search(
    connection: sqlite3.Connection, query: str, limit: int = 5, bbox: str | None = None
) -> list[tuple]:
    if not 1 <= limit <= 10:
        raise ValueError("Limit must be between 1 and 10")
    tokens = normalize(query).split()
    if not tokens:
        return []
    expression = " AND ".join(f'"{token}"*' for token in tokens)
    condition = ""
    parameters: list[str | float | int] = [expression]
    if bbox is not None:
        west, south, east, north = map(float, bbox.split(","))
        condition = " AND a.longitude BETWEEN ? AND ? AND a.latitude BETWEEN ? AND ?"
        parameters.extend([west, east, south, north])
    parameters.append(limit)
    return connection.execute(
        "SELECT a.address, a.latitude, a.longitude, a.parcel_id FROM addresses_fts "
        "JOIN addresses a ON a.id = addresses_fts.rowid WHERE addresses_fts MATCH ? "
        + condition
        + " ORDER BY bm25(addresses_fts), a.address, a.id LIMIT ?",
        parameters,
    ).fetchall()
