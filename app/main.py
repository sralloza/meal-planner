"""Main app generation."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette_prometheus import PrometheusMiddleware, metrics

from .api import router as api_router
from .core.config import settings
from .cron import scheduler, update_notion_meals
from .db.utils import create_db_and_tables
from .utils.misc import get_version
from .utils.server import catch_errors

# https://github.com/long2ice/fastapi-cache
# https://github.com/perdy/starlette-prometheus


def get_application():
    """Creates and sets up the application."""
    _app = FastAPI(
        title="Meal Planner", docs_url=None, redoc_url="/docs", version=get_version()
    )

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    _app.include_router(api_router)
    _app.add_exception_handler(500, catch_errors)

    if settings.ENABLE_PROMETHEUS:
        _app.add_middleware(PrometheusMiddleware)
        _app.add_route("/metrics/", metrics)

    @_app.on_event("startup")
    def on_startup():
        create_db_and_tables()

        if not settings.PRODUCTION:
            print(
                "Warning: development env, skipping "
                "cronjobs and initial notion update"
            )
            return

        if settings.DISABLE_CRON_INTEGRATION:
            print("Cron integration is disabled")
        else:
            scheduler.print_jobs()
            scheduler.start()

        update_notion_meals()

    return _app


app = get_application()
