import asyncio
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from routers.analyze_router import router

asyncio.set_event_loop_policy(
    asyncio.WindowsSelectorEventLoopPolicy()
)

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.include_router(router)

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )