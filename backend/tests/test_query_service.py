from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import create_engine, text

from dbviewer.query_service import QueryError, fetch_filtered_rows


@pytest.fixture()
def engine(tmp_path):
    db_path = tmp_path / "q.db"
    eng = create_engine(f"sqlite:///{db_path}")
    with eng.begin() as conn:
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
        conn.execute(text("INSERT INTO Customer VALUES (1,'Brazil','X');"))
    try:
        yield eng
    finally:
        eng.dispose()


def test_happy_path(engine):
    out = fetch_filtered_rows(
        engine,
        table_name="Customer",
        column_name="Country",
        value="Brazil",
        max_rows=50,
    )
    assert not isinstance(out, QueryError)
    assert "Country" in out.columns
    assert len(out.rows) == 1
    row = dict(zip(out.columns, out.rows[0]))
    assert row["Country"] == "Brazil"


def test_case_insensitive_table_and_column(engine):
    out = fetch_filtered_rows(
        engine,
        table_name="customer",
        column_name="country",
        value="Brazil",
        max_rows=50,
    )
    assert not isinstance(out, QueryError)
    assert len(out.rows) == 1


def test_unknown_table(engine):
    out = fetch_filtered_rows(
        engine,
        table_name="Nope",
        column_name="x",
        value="y",
        max_rows=50,
    )
    assert isinstance(out, QueryError)
    assert out.code == "unknown_table"


def test_unknown_column(engine):
    out = fetch_filtered_rows(
        engine,
        table_name="Customer",
        column_name="Nope",
        value="x",
        max_rows=50,
    )
    assert isinstance(out, QueryError)
    assert out.code == "unknown_column"


def test_respects_limit(tmp_path: Path):
    db_path = tmp_path / "lim.db"
    eng = create_engine(f"sqlite:///{db_path}")
    try:
        with eng.begin() as conn:
            conn.execute(text("CREATE TABLE T (Id INTEGER PRIMARY KEY, V TEXT);"))
            conn.execute(
                text(
                    "INSERT INTO T (V) VALUES "
                    + ",".join(["('x')"] * 20)
                )
            )
        out = fetch_filtered_rows(
            eng,
            table_name="T",
            column_name="V",
            value="x",
            max_rows=5,
        )
        assert not isinstance(out, QueryError)
        assert len(out.rows) == 5
    finally:
        eng.dispose()
