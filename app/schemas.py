from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, constr


class TaskStatus(str, Enum):
    """Статусы задач."""
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskBase(BaseModel):
    """Общие поля задачи."""
    name: constr(min_length=1, max_length=100) = Field(..., description="Короткое название")
    description: Optional[constr(max_length=2000)] = Field(None, description="Описание")


class TaskCreate(TaskBase):
    """Создание задачи."""
    status: TaskStatus = Field(default=TaskStatus.CREATED)


class TaskUpdate(BaseModel):
    """Частичное обновление."""
    name: Optional[constr(min_length=1, max_length=100)] = None
    description: Optional[constr(max_length=2000)] = None
    status: Optional[TaskStatus] = None
