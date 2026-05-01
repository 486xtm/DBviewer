"""Engine registration and request-scoped DB access."""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def includeme(config):
    settings = config.get_settings()
    url = settings["dbviewer.database_url"]
    extra: dict = {"pool_pre_ping": True}
    if url.startswith("sqlite:"):
        # Pool + Waitress threads: allow cross-thread checkout of SQLite connections.
        extra["connect_args"] = {"check_same_thread": False}
    engine = create_engine(url, **extra)
    config.registry["db_engine"] = engine

    def db_engine(request):
        return request.registry["db_engine"]

    config.add_request_method(db_engine, "db_engine", reify=True)
