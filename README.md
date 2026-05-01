# dbviewer

- **Backend:** Python 3, [Pyramid](https://trypyramid.com/), [SQLAlchemy](https://www.sqlalchemy.org/) (reflected tables), [Mako](https://www.makotemplates.org/) templates for the HTML shell.
- **Frontend:** React (Vite) — parses the URL path, loads JSON from the API, renders an HTML table.
- **Database:** SQLite **Chinook** sample (same idea as the interview links).

The `{database}` segment in the URL is kept for SlashDB parity (e.g. `Chinook`). With one SQLite file configured in `development.ini`, it does not switch databases; only `{table}`, `{column}`, and `{value}` drive the query.

---

## Project layout

| Path | Role |
|------|------|
| `backend/` | Pyramid app (`dbviewer` package), tests, `development.ini`, Chinook downloader |
| `backend/dbviewer/` | Routes, views, SQL reflection/query logic, static assets produced by the frontend build |
| `frontend/` | Vite + React source; `npm run build` writes into `backend/dbviewer/static/app/` |
| `backend/scripts/download_chinook.py` | Downloads `Chinook_Sqlite.sqlite` next to `development.ini` |

---

## Prerequisites

- **Python** 3.11+ (3.14 works if dependencies install cleanly).
- **Node.js** + npm — only needed to change the UI or rebuild assets (`npm run build`). Pre-built JS/CSS may already be present under `backend/dbviewer/static/app/`.

---

## Setup

### 1. Backend dependencies

From the **`backend`** directory:

```powershell
cd backend
python -m pip install -e ".[dev]"
```

The `[dev]` extra installs pytest, pytest-cov, and WebTest.

### 2. Chinook SQLite database

Still from **`backend`**:

```powershell
python scripts/download_chinook.py
```

This creates `backend/Chinook_Sqlite.sqlite` (skipped if the file already exists). The path is referenced from `development.ini` as `%(here)s/Chinook_Sqlite.sqlite`.

### 3. Frontend build (optional if assets already committed)

From **`frontend`**:

```powershell
cd frontend
npm install
npm run build
```

This refreshes `backend/dbviewer/static/app/` (JS/CSS the Pyramid shell loads).

---

## How to run

### Production-style (Pyramid serves everything)

From **`backend`**:

```powershell
cd backend
pserve development.ini
```

Then open:

- Example filtered page:  
  http://localhost:6543/db/Chinook/Customer/Country/Brazil.html  
- Same filter as JSON:  
  http://localhost:6543/api/db/Chinook/Customer/Country/Brazil  
- Short home link: http://localhost:6543/

**URL shape**

- HTML shell: `/db/{database}/{table}/{column}/{value}.html`
- JSON API: `/api/db/{database}/{table}/{column}/{value}`

Row count is capped by `dbviewer.max_rows` in `development.ini` (default `5000`).

### Frontend dev server (hot reload + proxy)

Use two terminals.

1. Backend:

   ```powershell
   cd backend
   pserve development.ini
   ```

2. Frontend:

   ```powershell
   cd frontend
   npm run dev
   ```

Vite proxies `/api`, `/db`, and `/static` to `http://127.0.0.1:6543`. Open the URL Vite prints (usually http://localhost:5173) and navigate to a path like `/db/Chinook/Customer/Country/Brazil.html`.

**If you still see a CORS error in dev:** restart **`pserve`** after pulling changes. `development.ini` sets `dbviewer.enable_cors = true`, which adds permissive `Access-Control-Allow-*` headers on Pyramid so the browser can call `http://localhost:6543` from another origin (for example if something bypasses the Vite proxy). For production, remove or set that flag to false.

---

## How to test

From **`backend`**:

```powershell
cd backend
python -m pytest
```

Defaults (see `pyproject.toml`) include coverage:

- Terminal summary with missing lines (`term-missing`)
- HTML report under **`backend/htmlcov/`** — open `htmlcov/index.html` in a browser

Useful variants:

```powershell
python -m pytest -v
python -m pytest tests/test_query_service.py
python -m pytest --no-cov
```

Tests use a **temporary SQLite file** with a tiny `Customer` table (no Chinook file required for CI/local pytest).

---

## Configuration highlights (`development.ini`)

| Setting | Meaning |
|---------|---------|
| `dbviewer.database_url` | SQLAlchemy URL (SQLite Chinook path by default) |
| `dbviewer.max_rows` | Maximum rows returned per request |
| `dbviewer.enable_cors` | When true, Pyramid sends permissive CORS headers (dev convenience; disable in production) |

SQLite is configured with `check_same_thread=False` in code so the pool works with a multi-threaded server (e.g. Waitress).

---

## Stretch behavior

Any **reflected table** and **existing column** on the configured database can be used in the URL; still **one equality filter** per request. Values are passed as bound parameters, not interpolated into SQL strings.
