from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.app.auth import auth
from src.db.main import init_db
from src.app.router import users, jobs, application
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

app.include_router(auth.auth_router, prefix=f'/api/{version}')
app.include_router(users.user_router, prefix=f'/api/{version}')
app.include_router(jobs.job_router, prefix=f'/api/{version}')
app.include_router(application.apps_router, prefix=f'/api/{version}')

@app.get('/')
async def root():
    return{"message":"Jobberman API"}