"""Dynamic single-column equality filter using reflected metadata."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence
from urllib.parse import unquote

from sqlalchemy import MetaData, Table, bindparam, inspect, select
from sqlalchemy.engine import Engine


@dataclass(frozen=True)
class FilteredResult:
    columns: list[str]
    rows: list[list[Any]]


@dataclass(frozen=True)
class QueryError:
    code: str
    message: str


def _resolve_table(engine: Engine, table_name: str) -> str | None:
    """Return the real table name as known to the backend (case-aware)."""
    insp = inspect(engine)
    names = insp.get_table_names()
    # Exact match first (Chinook uses PascalCase).
    if table_name in names:
        return table_name
    lower = {n.lower(): n for n in names}
    hit = lower.get(table_name.lower())
    return hit


def _resolve_column(table: Table, column_name: str) -> str | None:
    if column_name in table.c.keys():
        return column_name
    lower = {c.lower(): c for c in table.c.keys()}
    return lower.get(column_name.lower())


def fetch_filtered_rows(
    engine: Engine,
    *,
    table_name: str,
    column_name: str,
    value: str,
    max_rows: int,
) -> FilteredResult | QueryError:
    """
    Return up to ``max_rows`` rows where ``column_name`` equals the decoded
    ``value``. Table and column must exist on the configured database.
    Values are bound as parameters (no string interpolation into SQL).
    """
    resolved_table = _resolve_table(engine, table_name)
    if not resolved_table:
        return QueryError("unknown_table", f"Unknown table: {table_name!r}")

    md = MetaData()
    tbl = Table(resolved_table, md, autoload_with=engine)
    resolved_col = _resolve_column(tbl, column_name)
    if not resolved_col:
        return QueryError("unknown_column", f"Unknown column: {column_name!r}")

    col = tbl.c[resolved_col]
    raw = unquote(value)
    lim = max(1, min(int(max_rows), 1_000_000))
    stmt = select(tbl).where(col == bindparam("v")).limit(lim)

    with engine.connect() as conn:
        result = conn.execute(stmt, {"v": raw})
        colnames: Sequence[str] = list(result.keys())
        rows = [list(r) for r in result]

    return FilteredResult(columns=list(colnames), rows=rows)
