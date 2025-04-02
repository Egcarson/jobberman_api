from fastapi import FastAPI

version = "v1.0"

app = FastAPI(
    title="Jobberman API",
    description="REST API for job search web app",
    version=version
)