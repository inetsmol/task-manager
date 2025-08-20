from uuid import uuid4

from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator

from .schemas import TaskStatus


class Task(models.Model):
    """
    Таблица задач.
    """
    id = fields.UUIDField(pk=True, default=uuid4)
    name = fields.CharField(max_length=100)
    description = fields.TextField(null=True)
    status = fields.CharEnumField(TaskStatus, default=TaskStatus.CREATED)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self) -> str:
        return f"<Task {self.id} {self.name!r} {self.status}>"


TaskOut = pydantic_model_creator(Task, name="TaskOut")