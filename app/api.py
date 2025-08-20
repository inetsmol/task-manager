from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from tortoise.expressions import Q

from .models import Task, TaskOut
from .schemas import TaskCreate, TaskStatus, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(payload: TaskCreate) -> TaskOut:
    """
    Создаёт задачу.
    По умолчанию статус `created`.
    """
    obj = await Task.create(
        name=payload.name,
        description=payload.description,
        status=payload.status,
    )
    return await TaskOut.from_tortoise_orm(obj)


@router.get("/{task_id}", response_model=TaskOut)
async def get_task(task_id: UUID) -> TaskOut:
    """Возвращает задачу по UUID."""
    obj = await Task.get_or_none(id=task_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Task not found")
    return await TaskOut.from_tortoise_orm(obj)


@router.get("", response_model=List[TaskOut])
async def list_tasks(
    status_: Optional[TaskStatus] = Query(None, alias="status", description="Фильтр по статусу"),
    q: Optional[str] = Query(None, description="Поиск по подстроке в названии/описании"),
    limit: int = Query(100, ge=1, le=1000, description="Размер страницы (кол-во элементов)"),
    page: int = Query(1, ge=1, description="Номер страницы, начиная с 1"),
) -> List[TaskOut]:
    """
    Возвращает список задач с фильтрами и постраничной пагинацией.
    """
    offset = (page - 1) * limit

    qs = Task.all()
    if status_:
        qs = qs.filter(status=status_)
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
    qs = qs.offset(offset).limit(limit)

    return await TaskOut.from_queryset(qs)


@router.patch("/{task_id}", response_model=TaskOut)
async def update_task(task_id: UUID, patch: TaskUpdate) -> TaskOut:
    """Частичное обновление полей задачи."""
    obj = await Task.get_or_none(id=task_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Task not found")

    if patch.name is not None:
        obj.name = patch.name
    if patch.description is not None:
        obj.description = patch.description
    if patch.status is not None:
        obj.status = patch.status

    await obj.save()
    return await TaskOut.from_tortoise_orm(obj)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: UUID) -> None:
    obj = await Task.get_or_none(id=task_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Task not found")
    await obj.delete()
