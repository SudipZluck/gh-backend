from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.openapi.utils import get_openapi
from dotenv import load_dotenv

from db.sqlmodel import create_engine_from_env, dispose_engine
from sqlmodel import SQLModel, Session
from routers.user_routes import router as user_router
from routers.health_routes import router as health_router
from routers.journal_routes import router as journal_router
from routers.comment_routes import router as comment_router
from routers.social_routes import router as social_router
from routers.subscription_routes import router as subscription_router
from routers.prompt_routes import router as prompt_router
from routers.miscellaneous_routes import router as miscellaneous_router
from middleware.timing import TimingMiddleware
from middleware.exception_handlers import register_exception_handlers

load_dotenv()

# Security scheme for Bearer token
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    app.state.sql_engine = create_engine_from_env()
    # Auto-create tables at startup
    SQLModel.metadata.create_all(app.state.sql_engine)
    app.state.sql_session_factory = lambda: Session(app.state.sql_engine)
    try:
        yield
    finally:
        dispose_engine(app.state.sql_engine)


app = FastAPI(
    lifespan=lifespan,
    title="Grateful Hearts API",
    description="API for Grateful Hearts application",
    version="1.0.0",
    # openapi_tags=[
    #     {"name": "users", "description": "User management operations"},
    #     {"name": "auth", "description": "Authentication operations"},
    #     {"name": "journals", "description": "Journal management operations"},
    #     {"name": "comments", "description": "Comment management operations"},
    #     {"name": "social", "description": "Social features operations"},
    #     {"name": "subscriptions", "description": "Subscription management operations"},
    #     {"name": "prompts", "description": "Prompt management operations"},
    #     {"name": "miscellaneous", "description": "Miscellaneous operations"},
    #     {"name": "health", "description": "Health check operations"},
    # ]
)

# def custom_openapi():
#     if app.openapi_schema:
#         return app.openapi_schema

#     openapi_schema = get_openapi(
#         title=app.title,
#         version=app.version,
#         description=app.description,
#         routes=app.routes,
#     )

#     # Add security scheme
#     openapi_schema["components"]["securitySchemes"] = {
#         "BearerAuth": {
#             "type": "http",
#             "scheme": "bearer",
#             "bearerFormat": "JWT",
#         }
#     }

#     # Add security to all protected endpoints
#     for path in openapi_schema["paths"]:
#         for method in openapi_schema["paths"][path]:
#             if method.lower() in ["post", "put", "delete", "patch"]:
#                 # Skip login and signup endpoints
#                 if not any(skip_path in path for skip_path in ["/login", "/signup", "/forget-password", "/reset-password"]):
#                     if "security" not in openapi_schema["paths"][path][method]:
#                         openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]

#     app.openapi_schema = openapi_schema
#     return app.openapi_schema

# app.openapi = custom_openapi

register_exception_handlers(app)

app.include_router(user_router)
app.include_router(journal_router)
app.include_router(comment_router)
app.include_router(social_router)
app.include_router(subscription_router)
app.include_router(prompt_router)
app.include_router(miscellaneous_router)
app.include_router(health_router)


app.add_middleware(TimingMiddleware)

# if __name__ == "__main__":
#     uvicorn.run("main:app", host=HOST, port=PORT)