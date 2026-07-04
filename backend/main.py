import asyncio
import sys
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from database import init_db
from routers.analyze_router import router


if sys.platform.startswith("win") and hasattr(asyncio, "WindowsSelectorEventLoopPolicy"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Juez Bot")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app.include_router(router)


@app.on_event("startup")
def startup_event():
    try:
        init_db()
    except Exception as e:
        print(f"Aviso: no se pudo inicializar la base de datos: {e}")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {"request": request})


@app.get("/health")
def health():
    return {"status": "ok"}