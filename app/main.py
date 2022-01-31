import aioredis

from fastapi import FastAPI, Security
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from starlette.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi


from app.api.api import api_router
from app.core.config import settings
from app.core.security import get_api_key
from app.utils import utils

from app.api.endpoints.status import router

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

if settings.SSL_ENABLED:
    HTTP_URL = "https://" + settings.DOMAIN
else:
    HTTP_URL = "http://" + settings.DOMAIN

if settings.TARGET == "local":
    HTTP_URL = HTTP_URL + ":" + settings.PORT

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    BACKEND_CORS_ORIGINS = settings.BACKEND_CORS_ORIGINS
    if HTTP_URL not in settings.BACKEND_CORS_ORIGINS:
        BACKEND_CORS_ORIGINS.append(HTTPS_DOMAIN)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def custom_openapi(root_path):
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Notify-service FastAPI APP",
        version=app.version,
        description="Custom OpenAPI schema with code samples",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://raw.githubusercontent.com/waynesun09/notify-service/main/docs/static/notify-logo.png"
    }

    # Set servers in the schema
    server = {}
    openapi_schema["servers"] = []
    server["url"] = HTTP_URL
    server["description"] = "Service url"
    openapi_schema["servers"].append(server.copy())

    # Set language code samples
    openapi_schema = utils.add_examples(openapi_schema)
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

app.include_router(router, prefix="/status")
app.include_router(api_router, prefix=settings.API_V1_STR, dependencies=[Security(get_api_key)])


@app.on_event("startup")
async def startup():
    redis = aioredis.from_url(settings.REDIS_URI, password=settings.REDIS_PASSWORD, encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
