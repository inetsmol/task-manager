import os

from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from app.api import router as tasks_router

app = FastAPI(
    title="Task Manager API",
    version="0.3.0",
    description="Мини-сервис управления задачами (CRUD) на SQLite + Tortoise ORM.",
)


DB_URL = os.getenv("DATABASE_URL", "sqlite://tasks.db")


register_tortoise(
    app,
    db_url=DB_URL,
    modules={"models": ["app.models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)


app.include_router(tasks_router)


@app.get("/", tags=["health"])
async def root():
    """Health-check."""
    return {"status": "ok"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)