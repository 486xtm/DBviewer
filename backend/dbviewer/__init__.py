"""WSGI application package.

Design notes (uniform backends, mixed workloads)
-----------------------------------------------
SQLAlchemy provides a single API across SQLite, Postgres, Oracle, SQL Server,
etc. The dialect and connection URL choose the driver; we avoid bespoke SQL.

For production under mixed workloads (many tiny queries vs rare multi-minute
reports), typical mitigations live *outside* this minimal demo: PgBouncer or
similar pooler, separate read replicas or resource groups, ``statement_timeout``
per role (PostgreSQL), Oracle ``resource_manager``, and an async job queue for
explicitly long exports. For very long synchronous requests, consider streaming
responses and client timeouts so small fast traffic keeps using the main pool.

This app uses a bounded result set (``dbviewer.max_rows``) so pathological
full-table reads do not balloon memory. Tune pool sizes and timeouts via
``create_engine`` kwargs for your deployment.
"""

from pyramid.config import Configurator


def main(global_config, **settings):
    """PasteDeploy / ``pserve`` entry point."""
    # Filter out PasteDeploy-only keys if present
    settings = {k: v for k, v in settings.items() if not k.startswith("_")}
    config = Configurator(settings=settings)
    config.include("pyramid_mako")
    config.include(".db")
    config.include(".cors_tween")
    config.include(".routes")
    config.scan("dbviewer.views.views")
    return config.make_wsgi_app()
