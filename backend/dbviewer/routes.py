def includeme(config):
    config.add_static_view(
        name="static",
        path="dbviewer:static",
        cache_max_age=3600,
    )
    config.add_route("home", "/")
    config.add_route(
        "api_rows",
        r"/api/db/{database}/{table}/{column}/{value}",
    )
    config.add_route(
        "table_page",
        r"/db/{database}/{table}/{column}/{value}.html",
    )
