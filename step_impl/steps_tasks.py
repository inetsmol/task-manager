# step_impl/steps_tasks.py
"""
Простые Gauge-шаги для CRUD.
— Используем один глобальный TASK_ID вместо Datastore.
— Каждый шаг открывает свой httpx.AsyncClient поверх ASGI-приложения.
— Перед импортом приложения подменяем БД на тестовую (sqlite://test_tasks.db).
"""

from __future__ import annotations

import os
from pathlib import Path

import anyio
from getgauge.python import step
from httpx import ASGITransport, AsyncClient

# 1) Тестовая БД: отдельный файл и чистый старт
os.environ.setdefault("DATABASE_URL", "sqlite://test_tasks.db")
Path("test_tasks.db").unlink(missing_ok=True)

# 2) Импортируем само приложение FastAPI
from app.main import app

# 3) Глобальное хранилище id созданной задачи между шагами
TASK_ID: str | None = None


async def _client() -> AsyncClient:
    """
    Создаёт HTTPX-клиент поверх FastAPI-приложения (ASGITransport).
    Так не нужно поднимать uvicorn — тесты быстрые и изолированные.
    """
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    return AsyncClient(transport=transport, base_url="http://test")


@step('Создать задачу с именем "<name>" и описанием "<desc>"')
def create_task(name: str, desc: str) -> None:
    async def run() -> None:
        global TASK_ID
        async with await _client() as client:
            resp = await client.post("/tasks", json={"name": name, "description": desc})
            assert resp.status_code == 201, resp.text
            TASK_ID = resp.json()["id"]  # сохраняем для следующих шагов
    anyio.run(run)


@step('Получить эту задачу и ожидать статус "<status>" и имя "<name>"')
def get_and_expect(status: str, name: str) -> None:
    async def run() -> None:
        assert TASK_ID, "TASK_ID пуст — сперва вызовите шаг создания задачи"
        async with await _client() as client:
            resp = await client.get(f"/tasks/{TASK_ID}")
            assert resp.status_code == 200, resp.text
            body = resp.json()
            assert body["status"] == status
            assert body["name"] == name
    anyio.run(run)


@step('Обновить статус этой задачи на "<status>"')
def update_status(status: str) -> None:
    async def run() -> None:
        assert TASK_ID, "TASK_ID пуст — сперва вызовите шаг создания задачи"
        async with await _client() as client:
            resp = await client.patch(f"/tasks/{TASK_ID}", json={"status": status})
            assert resp.status_code == 200, resp.text
            assert resp.json()["status"] == status
    anyio.run(run)


@step('Проверить, что задача теперь со статусом "<status>"')
def check_status(status: str) -> None:
    async def run() -> None:
        assert TASK_ID, "TASK_ID пуст — сперва вызовите шаг создания задачи"
        async with await _client() as client:
            resp = await client.get(f"/tasks/{TASK_ID}")
            assert resp.status_code == 200, resp.text
            assert resp.json()["status"] == status
    anyio.run(run)


@step('Список задач должен содержать "<name_substr>"')
def list_contains(name_substr: str) -> None:
    async def run() -> None:
        async with await _client() as client:
            # Пагинация теперь по page; для проверки поиска это не важно.
            resp = await client.get("/tasks", params={"q": name_substr})
            assert resp.status_code == 200, resp.text
            names = [x["name"] for x in resp.json()]
            assert any(name_substr in n for n in names), f"{name_substr!r} не найдено в {names}"
    anyio.run(run)


@step("Удалить эту задачу")
def delete_task() -> None:
    async def run() -> None:
        assert TASK_ID, "TASK_ID пуст — сперва вызовите шаг создания задачи"
        async with await _client() as client:
            resp = await client.delete(f"/tasks/{TASK_ID}")
            assert resp.status_code == 204, resp.text
    anyio.run(run)


@step("Попытка получить удалённую задачу должна вернуть 404")
def get_should_be_404() -> None:
    async def run() -> None:
        assert TASK_ID, "TASK_ID пуст — сперва вызовите шаг создания задачи"
        async with await _client() as client:
            resp = await client.get(f"/tasks/{TASK_ID}")
            assert resp.status_code == 404, resp.text
    anyio.run(run)
