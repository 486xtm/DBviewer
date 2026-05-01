from __future__ import annotations

import pytest
from sqlalchemy import create_engine, text
from webtest import TestApp

from dbviewer import main


@pytest.fixture()
def sqlite_app(tmp_path):
    db_path = tmp_path / "t.db"
    engine = create_engine(f"sqlite:///{db_path}")
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE Customer (
                  CustomerId INTEGER PRIMARY KEY,
                  Country TEXT,
                  City TEXT
                );
                """
            )
        )
        conn.execute(
            text(
                "INSERT INTO Customer VALUES "
                "(1,'Brazil','Sao Paulo'),(2,'Czech Republic','Prague');"
            )
        )

    settings = {
        "dbviewer.database_url": f"sqlite:///{db_path}",
        "dbviewer.max_rows": "100",
    }
    wsgi = main({}, **settings)
    try:
        yield TestApp(wsgi)
    finally:
        wsgi.registry["db_engine"].dispose()
