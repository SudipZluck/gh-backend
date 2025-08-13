from contextlib import asynccontextmanager

from fastapi import FastAPI
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


app = FastAPI(lifespan=lifespan)

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