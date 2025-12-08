from fastapi import APIRouter, HTTPException, Query, Security, status
from typing import List, Optional
from sqlmodel import select, Session
from sqlalchemy import cast, func
from sqlalchemy.dialects.postgresql import JSONB
from app.core.security import get_api_key
from app.db import engine
from app.models import Todo
from app.schemas import TodoCreate, TodoRead, TodoUpdate
from uuid import UUID
from datetime import datetime, timezone

router = APIRouter(
    prefix="/todos",
    tags=["todos"],
    responses={
        401: {"description": "Unauthorized - Missing API key header"},
        403: {"description": "Forbidden - Invalid API key"},
        404: {"description": "Not found"},
    }
)


@router.post(
    "/",
    response_model=TodoRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Security(get_api_key)],
    summary="Create a new todo",
    description="Create a new todo item with title, description, due date, priority, and tags.",
    response_description="The created todo item"
)
def create_todo(item: TodoCreate):
    """
    Create a new todo item.
    
    - **title**: Required. The title of the todo
    - **description**: Optional. Detailed description
    - **due_at**: Optional. Due date and time
    - **estimated_minutes**: Optional. Estimated completion time
    - **priority**: Optional. Priority level (1-5, default: 3)
    - **tags**: Optional. List of tags for categorization
    
    Returns the created todo with generated ID and timestamps.
    """
    todo = Todo(**item.model_dump())
    with Session(engine) as session:
        session.add(todo)
        session.commit()
        session.refresh(todo)
    return todo


@router.get(
    "/",
    response_model=List[TodoRead],
    dependencies=[Security(get_api_key)],
    summary="List todos",
    description="Retrieve a list of todos with optional filtering and search capabilities.",
    response_description="List of todo items matching the criteria"
)
def list_todos(
    q: Optional[str] = Query(None, description="Search query to filter todos by title (case-insensitive partial match)", example="project"),
    tag: Optional[str] = Query(None, description="Filter todos by a specific tag", example="work"),
    status: Optional[str] = Query(None, description="Filter todos by status (e.g., 'todo', 'in_progress', 'done')", example="todo"),
    limit: int = Query(100, le=1000, description="Maximum number of todos to return (max: 1000)", example=50),
):
    """
    List all todos with optional filtering.
    
    Query parameters:
    - **q**: Search todos by title (partial match, case-insensitive)
    - **tag**: Filter by a specific tag
    - **status**: Filter by status
    - **limit**: Maximum number of results (default: 100, max: 1000)
    
    All filters can be combined. Returns an empty list if no todos match.
    """
    with Session(engine) as session:
        statement = select(Todo)
        if q:
            statement = statement.where(Todo.title.ilike(f"%{q}%"))
        if tag:
            # Use PostgreSQL JSONB @> operator to check if array contains the tag
            # This works for PostgreSQL; for SQLite, tags would need to be filtered differently
            # jsonb_build_array creates a JSONB array with the tag value
            statement = statement.where(cast(Todo.tags, JSONB).op('@>')(func.jsonb_build_array(tag)))
        if status:
            statement = statement.where(Todo.status == status)
        statement = statement.limit(limit)
        results = list(session.exec(statement).all())
    return results


@router.get(
    "/{item_id}",
    response_model=TodoRead,
    dependencies=[Security(get_api_key)],
    summary="Get a todo by ID",
    description="Retrieve a specific todo item by its unique identifier.",
    response_description="The todo item",
    responses={
        404: {"description": "Todo not found"}
    }
)
def get_todo(item_id: UUID):
    """
    Get a specific todo by its ID.
    
    - **item_id**: The UUID of the todo to retrieve
    
    Returns 404 if the todo is not found.
    """
    with Session(engine) as session:
        todo = session.get(Todo, item_id)
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@router.patch(
    "/{item_id}",
    response_model=TodoRead,
    dependencies=[Security(get_api_key)],
    summary="Update a todo",
    description="Partially update a todo item. Only provided fields will be updated.",
    response_description="The updated todo item",
    responses={
        404: {"description": "Todo not found"}
    }
)
def update_todo(item_id: UUID, patch: TodoUpdate):
    """
    Partially update a todo item.
    
    - **item_id**: The UUID of the todo to update
    - **patch**: TodoUpdate object with fields to update (all fields optional)
    
    Only the fields provided in the request body will be updated.
    The `updated_at` timestamp is automatically set to the current time.
    
    Returns 404 if the todo is not found.
    """
    with Session(engine) as session:
        todo = session.get(Todo, item_id)
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        data = patch.model_dump(exclude_unset=True)
        for k, v in data.items():
            setattr(todo, k, v)
        todo.updated_at = datetime.now(timezone.utc)
        session.add(todo)
        session.commit()
        session.refresh(todo)
    return todo


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Security(get_api_key)],
    summary="Delete a todo",
    description="Delete a todo item by its unique identifier.",
    response_description="No content on successful deletion",
    responses={
        404: {"description": "Todo not found"}
    }
)
def delete_todo(item_id: UUID):
    """
    Delete a todo item.
    
    - **item_id**: The UUID of the todo to delete
    
    Returns 204 No Content on successful deletion.
    Returns 404 if the todo is not found.
    """
    with Session(engine) as session:
        todo = session.get(Todo, item_id)
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        session.delete(todo)
        session.commit()
    return None
