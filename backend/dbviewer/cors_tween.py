"""Optional CORS headers for local dev (e.g. browser page on Vite, API on Pyramid)."""

from __future__ import annotations

from pyramid.response import Response


def _truthy(raw: object) -> bool:
    if raw is None:
        return False
    return str(raw).lower() in ("1", "true", "yes", "on")


def cors_tween_factory(handler, registry):
    """Pyramid tween factory; disabled unless ``dbviewer.enable_cors`` is set."""
    if not _truthy(registry.settings.get("dbviewer.enable_cors")):
        return handler

    def cors_tween(request):
        def apply_headers(resp: Response) -> None:
            resp.headers["Access-Control-Allow-Origin"] = "*"
            resp.headers["Access-Control-Allow-Methods"] = "GET, HEAD, OPTIONS"
            req_h = request.headers.get("Access-Control-Request-Headers")
            resp.headers["Access-Control-Allow-Headers"] = req_h or "*"

        if request.method == "OPTIONS":
            resp = Response(status=204)
            apply_headers(resp)
            return resp

        response = handler(request)
        apply_headers(response)
        return response

    return cors_tween


def includeme(config):
    settings = config.get_settings()
    if _truthy(settings.get("dbviewer.enable_cors")):
        config.add_tween("dbviewer.cors_tween.cors_tween_factory")
