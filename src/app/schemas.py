from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


class TodoCreate(BaseModel):
    """Schema for creating a new todo item."""
    title: str = Field(..., description="The title of the todo item", example="Complete project documentation")
    description: Optional[str] = Field(None, description="Detailed description of the todo", example="Write comprehensive API documentation with examples")
    due_at: Optional[datetime] = Field(None, description="Due date and time for the todo", example="2024-12-31T23:59:59")
    estimated_minutes: Optional[int] = Field(None, description="Estimated time to complete in minutes", example=120, ge=0)
    priority: Optional[int] = Field(3, description="Priority level (1=highest, 5=lowest)", example=2, ge=1, le=5)
    tags: Optional[List[str]] = Field(None, description="List of tags for categorizing the todo", example=["work", "urgent", "documentation"])

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Complete project documentation",
                "description": "Write comprehensive API documentation with examples",
                "due_at": "2024-12-31T23:59:59",
                "estimated_minutes": 120,
                "priority": 2,
                "tags": ["work", "urgent", "documentation"]
            }
        }


class TodoRead(TodoCreate):
    """Schema for reading a todo item with all fields including metadata."""
    id: UUID = Field(..., description="Unique identifier for the todo item", example="123e4567-e89b-12d3-a456-426614174000")
    created_at: datetime = Field(..., description="Timestamp when the todo was created", example="2024-01-15T10:30:00")
    updated_at: Optional[datetime] = Field(None, description="Timestamp when the todo was last updated", example="2024-01-16T14:20:00")
    status: Optional[str] = Field("todo", description="Status of the todo (e.g., 'todo', 'in_progress', 'done')", example="todo")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Complete project documentation",
                "description": "Write comprehensive API documentation with examples",
                "due_at": "2024-12-31T23:59:59",
                "estimated_minutes": 120,
                "status": "todo",
                "priority": 2,
                "tags": ["work", "urgent", "documentation"],
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-16T14:20:00"
            }
        }


class TodoUpdate(BaseModel):
    """Schema for updating a todo item. All fields are optional."""
    title: Optional[str] = Field(None, description="The title of the todo item", example="Updated project documentation")
    description: Optional[str] = Field(None, description="Detailed description of the todo", example="Updated description")
    due_at: Optional[datetime] = Field(None, description="Due date and time for the todo", example="2024-12-31T23:59:59")
    estimated_minutes: Optional[int] = Field(None, description="Estimated time to complete in minutes", example=90, ge=0)
    status: Optional[str] = Field(None, description="Status of the todo (e.g., 'todo', 'in_progress', 'done')", example="in_progress")
    priority: Optional[int] = Field(None, description="Priority level (1=highest, 5=lowest)", example=1, ge=1, le=5)
    tags: Optional[List[str]] = Field(None, description="List of tags for categorizing the todo", example=["work", "completed"])

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Updated project documentation",
                "status": "in_progress",
                "priority": 1,
                "tags": ["work", "completed"]
            }
        }
