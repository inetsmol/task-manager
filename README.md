# Task Manager (FastAPI + Tortoise ORM + SQLite + Gauge)

Небольшой сервис «Менеджер задач» с CRUD-операциями, Swagger-документацией, Docker-окружением и автотестами на Gauge.

---

## Возможности

- CRUD для задач: `uuid`, `name`, `description`, `status ∈ {created, in_progress, completed}`
- Фильтр по статусу и поиск по подстроке (`q`)
- Пагинация по **номеру страницы**: `page` (с 1) + `limit`
- Автогенерация схем БД при старте (Tortoise + SQLite)
- Swagger/OpenAPI: `/docs` и `/openapi.json`
- Автотесты на Gauge (спеки), отдельная тестовая БД
- Docker для сервиса и для прогона тестов

---

## Стек

- **FastAPI** (async HTTP API)  
- **Tortoise ORM** + **aiosqlite** (SQLite-файл)  
- **Pydantic v2** (валидация)  
- **HTTPX (ASGITransport)** — тестовый HTTP-клиент «в памяти»  
- **Gauge** — BDD-спеки и шаги на Python

---

## Требования

- Python **3.11+**
- (опционально) Docker 24+
- (для тестов) Gauge CLI + плагин `python`

---

## Установка и запуск (локально)

```bash
# 1) Клонируйте код и перейдите в папку проекта
git clone <repo-url> task-manager
cd task-manager

# 2) Виртуальное окружение
python -m venv .venv
# Windows:
# .venv\Scripts\activate
# Linux/macOS:
. .venv/bin/activate

# 3) Зависимости
pip install -U pip
pip install -r requirements.txt

# 4) Запуск сервера разработки
uvicorn app.main:app --reload
# Swagger: http://localhost:8000/docs
```

### Конфигурация БД

По умолчанию используется файл рядом с приложением: `sqlite://tasks.db`.

Переопределение через переменную окружения:

```bash
# Linux/macOS
export DATABASE_URL="sqlite:///absolute/path/to/my_tasks.db"
uvicorn app.main:app --reload

# PowerShell (Windows)
$env:DATABASE_URL = "sqlite://C:/path/to/my_tasks.db"
uvicorn app.main:app --reload
```

> Схемы создаются автоматически при старте.

---

## API

### Модель `Task` (ответ)

```json
{
  "id": "1f4f1a2a-c2b0-4a00-b3bb-0f9bd3a8d9f1",
  "name": "Buy milk",
  "description": "2 liters",
  "status": "created",           // created | in_progress | completed
  "created_at": "2025-08-20T05:00:00+00:00",
  "updated_at": "2025-08-20T05:00:00+00:00"
}
```

### Эндпоинты

- **POST `/tasks`** — создать задачу  
  Тело (пример):
  ```json
  {"name":"Buy milk","description":"2 liters","status":"created"}
  ```
  По умолчанию `status = "created"`.

- **GET `/tasks/{id}`** — получить задачу по `UUID`

- **GET `/tasks`** — список задач  
  Параметры:
  - `status` — фильтр по статусу (опционально)
  - `q` — поиск по подстроке в `name`/`description` (опционально)
  - `limit` — размер страницы (по умолчанию 100, диапазон 1..1000)
  - `page` — **номер страницы** (начиная с 1)

- **PATCH `/tasks/{id}`** — частичное обновление  
  Тело: любой поднабор из `name`, `description`, `status`

- **DELETE `/tasks/{id}`** — удалить (204)

### Примеры cURL

```bash
# Создать
curl -X POST http://localhost:8000/tasks   -H "Content-Type: application/json"   -d '{"name":"Buy milk","description":"2 liters"}'

# Получить
curl http://localhost:8000/tasks/<UUID>

# Список (поиск + пагинация: 50 элементов на 2-й странице)
curl "http://localhost:8000/tasks?q=milk&limit=50&page=2"

# Обновить статус
curl -X PATCH http://localhost:8000/tasks/<UUID>   -H "Content-Type: application/json"   -d '{"status":"in_progress"}'

# Удалить
curl -X DELETE http://localhost:8000/tasks/<UUID>
```

---

## Тесты (Gauge)

В проекте есть:
- `specs/tasks.spec` - сценарий теста (BDD)
- `step_impl/steps_tasks.py` - шаги

Шаги запускают FastAPI-приложение «в памяти» (HTTPX ASGITransport).  
Для тестов используется отдельная БД: `sqlite://test_tasks.db`.

### Установка Gauge

```bash
# macOS/Linux
curl -SsL https://downloads.gauge.org/stable | sh
gauge install python
```

### Запуск тестов

```bash
# (рекомендуется активное виртуальное окружение)
gauge run specs
# HTML-отчёт, если подключён плагин html-report (см. manifest.json), появится в ./reports
```

---

## Docker

### Сервис

```bash
# Сборка
docker build -t task-manager .

# Запуск
docker run --rm -p 8000:8000 task-manager
# Swagger: http://localhost:8000/docs
```

Переопределение БД:

```bash
docker run --rm -p 8000:8000   -e DATABASE_URL="sqlite://tasks.db"   task-manager
```

### Тесты в Docker

```bash
# Сборка контейнера с Gauge
docker build -f Dockerfile.tests -t task-manager-tests .

# Запуск тестов (с сохранением отчётов на хосте)
docker run --rm -v "$PWD/reports:/project/reports" task-manager-tests
```

---

## Замечания по реализации

- Возвращаем **Pydantic-модели** (`response_model`), а не ORM-объекты → корректная сериализация и OpenAPI
- Разделяем ORM и публичные схемы — безопаснее и гибче
- Тесты не поднимают Uvicorn — быстрее и стабильнее
- Для простоты миграции не используются (схемы создаются автоматически при старте)

---

## Возможные расширения

- Валидация переходов статусов (например, запрет `completed → in_progress`)
- Индексы по `status`/`name` (для больших объёмов)
- Миграции через `aerich`, если появится потребность
- Авторизация/аутентификация пользователей, разграничение прав

---
