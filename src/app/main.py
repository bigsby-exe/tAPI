from fastapi import FastAPI
from app.api import todos
from app.db import create_db_and_tables

app = FastAPI(
    title="tAPI - Todo API",
    description="""
    A RESTful API for managing todos with features including:
    
    * **Create** todos with title, description, due dates, and tags
    * **List** todos with filtering and search capabilities
    * **Update** todo items
    * **Delete** todos
    
    All endpoints require API key authentication via the `X-API-Key` header.
    """,
    version="1.0.0",
    contact={
        "name": "tAPI Support",
    },
    license_info={
        "name": "MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


@app.on_event("startup")
def on_startup():
    # create DB tables if they do not exist
    create_db_and_tables()


app.include_router(todos.router)


@app.get(
    "/health",
    tags=["health"],
    summary="Health check endpoint",
    description="Returns the health status of the API",
    response_description="API health status"
)
def health():
    """
    Health check endpoint to verify the API is running.
    
    Returns:
        dict: Status object with "ok" status
    """
    return {"status": "ok"}
