import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from src import api_router
from src.config import settings


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Web Content Vectorization Service API",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# Set security middlewares for production environments
if settings.ENVIRONMENT == "production":
    # Force HTTPS in production
    app.add_middleware(HTTPSRedirectMiddleware)
    
    # Validate host headers to prevent Host header attacks
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=["api.example.com", "*.example.com"]
    )

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)
