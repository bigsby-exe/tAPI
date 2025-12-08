from typing import Optional, List
from sqlmodel import SQLModel, Field, Column
from datetime import datetime, timezone
from sqlalchemy import JSON
from uuid import UUID, uuid4


class TodoBase(SQLModel):
    title: str
    description: Optional[str] = None
    due_at: Optional[datetime] = None
    estimated_minutes: Optional[int] = None
    status: Optional[str] = "todo"
    priority: Optional[int] = 3
    tags: Optional[List[str]] = None


class Todo(TodoBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    tags: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
