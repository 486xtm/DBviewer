"""HTTP views for HTML shell and JSON API."""

from __future__ import annotations

from pyramid.request import Request
from pyramid.view import view_config

from dbviewer.query_service import QueryError, fetch_filtered_rows


def _max_rows(request: Request) -> int:
    raw = request.registry.settings.get("dbviewer.max_rows", "5000")
    try:
        return int(raw)
    except (TypeError, ValueError):
        return 5000


@view_config(route_name="home", renderer="dbviewer:templates/home.mako")
def home(request: Request):
    return {"example_path": "/db/Chinook/Customer/Country/Brazil.html"}


@view_config(route_name="table_page", renderer="dbviewer:templates/spa.mako")
def table_page(request: Request):
    """Serve React bootstrap shell; client reads pathname and calls JSON API."""
    return {
        "asset_css": request.static_url(
            "dbviewer:static/app/assets/index.css",
        ),
        "asset_js": request.static_url(
            "dbviewer:static/app/assets/index.js",
        ),
    }


@view_config(route_name="api_rows", renderer="json")
def api_rows(request: Request):
    """SlashDB-style JSON for any reflected table / column (single equality)."""
    engine = request.db_engine
    database = request.matchdict["database"]
    table = request.matchdict["table"]
    column = request.matchdict["column"]
    value = request.matchdict["value"]
    max_rows = _max_rows(request)

    out = fetch_filtered_rows(
        engine,
        table_name=table,
        column_name=column,
        value=value,
        max_rows=max_rows,
    )
    if isinstance(out, QueryError):
        code = 404 if out.code in {"unknown_table", "unknown_column"} else 400
        request.response.status = code
        return {
            "error": out.code,
            "message": out.message,
            "database": database,
            "table": table,
            "column": column,
            "value": value,
        }

    return {
        "database": database,
        "table": table,
        "column": column,
        "value": value,
        "columns": out.columns,
        "rows": out.rows,
        "truncated_hint": len(out.rows) >= max_rows,
    }
