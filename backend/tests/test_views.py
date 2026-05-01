from __future__ import annotations

from types import SimpleNamespace

from pyramid.testing import DummyRequest

from dbviewer.views.views import _max_rows


def test_max_rows_invalid_setting_returns_default():
    req = DummyRequest()
    req.registry = SimpleNamespace(
        settings={"dbviewer.max_rows": "not-a-number"}
    )
    assert _max_rows(req) == 5000


def test_max_rows_valid_setting():
    req = DummyRequest()
    req.registry = SimpleNamespace(settings={"dbviewer.max_rows": "42"})
    assert _max_rows(req) == 42


def test_api_country_brazil(sqlite_app):
    r = sqlite_app.get("/api/db/Chinook/Customer/Country/Brazil", status=200)
    body = r.json
    assert body["table"] == "Customer"
    assert body["column"] == "Country"
    assert body["rows"]
    assert len(body["rows"]) == 1


def test_api_city_prague(sqlite_app):
    r = sqlite_app.get("/api/db/Chinook/Customer/City/Prague", status=200)
    assert len(r.json["rows"]) == 1


def test_api_unknown_table(sqlite_app):
    r = sqlite_app.get("/api/db/Chinook/MissingTbl/Country/Brazil", status=404)
    assert r.json["error"] == "unknown_table"


def test_table_page_shell(sqlite_app):
    # Shell references static assets; may 404 CSS/JS if frontend not built.
    r = sqlite_app.get("/db/Chinook/Customer/Country/Brazil.html", status=200)
    assert b"root" in r.body


def test_home(sqlite_app):
    r = sqlite_app.get("/", status=200)
    assert b"Brazil" in r.body
