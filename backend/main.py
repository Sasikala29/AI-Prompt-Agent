from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.api.agent import router as agent_router
from backend.api.chat import router as chat_router
from backend.api.comparison import router as comparison_router
from backend.api.prompts import router as prompts_router
from backend.api.database_viewer import router as database_router
from backend.core.config import settings
from backend.database.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="AI Prompt Engineering and Mistral-based LLM experimentation platform.",
    lifespan=lifespan,
)

frontend_path = Path(__file__).resolve().parent.parent / "frontend"

app.mount(
    "/frontend",
    StaticFiles(directory=frontend_path),
    name="frontend",
)

app.include_router(prompts_router)
app.include_router(comparison_router)
app.include_router(chat_router)
app.include_router(agent_router)
app.include_router(database_router)


@app.get("/")
async def root():
    return FileResponse(frontend_path / "index.html")


@app.get("/health")
async def health():
    return {"status": "healthy"}
