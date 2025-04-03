from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.db.main import init_db

@asynccontextmanager
async def life_span(app: FastAPI):
    print (f"sever is starting ..........")
    await init_db()
    yield
    print (f"sever is shutting down ..........")
    print (f"sever has been stopped")

version = "v1.0"

app = FastAPI(
    title="Jobberman API",
    description="REST API for job search web app",
    version=version,
    lifespan=life_span
)