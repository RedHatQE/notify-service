import aioredis

from fastapi import FastAPI, Security
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from starlette.middleware.cors import CORSMiddleware

from app.api.api import api_router
from app.core.config import settings
from app.core.security import get_api_key

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR, dependencies=[Security(get_api_key)])

@app.on_event("startup")
async def startup():
    redis = await aioredis.create_redis_pool(settings.REDIS_URI, password=settings.REDIS_PASSWORD, encoding="utf8")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
