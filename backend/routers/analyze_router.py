from pathlib import Path
import base64
import os
import shutil
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, Form, Request
from fastapi.templating import Jinja2Templates

from config import BASE_DIR, VIDEO_FOLDER
from database import save_analysis, get_historial
from services.gemini_service import analyze_video
from services.parser_service import parse_result

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

LAST_VIDEO_TIME = None
LAST_VIDEO_NAME = None
IS_RECORDING = False
IS_PAUSED = False

VIDEO_DIR = Path(VIDEO_FOLDER)
VIDEO_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/check_status")
def check_status():
    if LAST_VIDEO_TIME is None:
        return {"ready": False}

    return {
        "ready": True,
        "video": LAST_VIDEO_NAME,
        "hora": LAST_VIDEO_TIME.strftime("%H:%M:%S"),
    }


@router.get("/start_recording")
def start_recording():
    global IS_RECORDING, IS_PAUSED

    IS_RECORDING = True
    IS_PAUSED = False

    return {
        "recording": IS_RECORDING,
        "paused": IS_PAUSED,
    }


@router.get("/pause_recording")
def pause_recording():
    global IS_RECORDING, IS_PAUSED

    if IS_RECORDING and not IS_PAUSED:
        IS_PAUSED = True

    return {
        "recording": IS_RECORDING,
        "paused": IS_PAUSED,
    }


@router.get("/resume_recording")
def resume_recording():
    global IS_RECORDING, IS_PAUSED

    if IS_RECORDING and IS_PAUSED:
        IS_PAUSED = False

    return {
        "recording": IS_RECORDING,
        "paused": IS_PAUSED,
    }


@router.get("/stop_recording")
def stop_recording():
    global IS_RECORDING, IS_PAUSED

    IS_RECORDING = False
    IS_PAUSED = False

    return {
        "recording": IS_RECORDING,
        "paused": IS_PAUSED,
    }


@router.get("/recording_status")
def recording_status():
    return {
        "recording": IS_RECORDING,
        "paused": IS_PAUSED,
    }


@router.post("/upload")
async def upload_video(video: UploadFile = File(...)):
    global LAST_VIDEO_TIME, LAST_VIDEO_NAME

    filename = f"fight_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    path = VIDEO_DIR / filename

    with path.open("wb") as buffer:
        shutil.copyfileobj(video.file, buffer)

    LAST_VIDEO_TIME = datetime.now()
    LAST_VIDEO_NAME = filename

    return {
        "mensaje": "ok",
        "video": filename,
    }


def file_to_base64(file: UploadFile):
    if file and file.filename:
        data = file.file.read()
        return base64.b64encode(data).decode(), file.content_type

    return None, None


@router.post("/analyze")
async def analyze(
    request: Request,
    robot_a: str = Form(...),
    robot_b: str = Form(...),
    video: UploadFile = File(None),
    img_a_inicio: UploadFile = File(None),
    img_a_final: UploadFile = File(None),
    img_b_inicio: UploadFile = File(None),
    img_b_final: UploadFile = File(None),
):
    global LAST_VIDEO_NAME, LAST_VIDEO_TIME

    try:
        if video and video.filename:
            LAST_VIDEO_NAME = None
            LAST_VIDEO_TIME = None

            filename = f"fight_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
            path = VIDEO_DIR / filename

            with path.open("wb") as buffer:
                shutil.copyfileobj(video.file, buffer)

        else:
            videos = sorted(VIDEO_DIR.glob("*.mp4"), key=os.path.getmtime)

            if not videos:
                raise Exception("No hay videos disponibles")

            path = videos[-1]
            filename = path.name

    except Exception as e:
        return templates.TemplateResponse(
            request,
            "index.html",
            {
                "request": request,
                "error": f"Error con el video: {str(e)}",
            },
        )

    img_ai_b64, img_ai_type = file_to_base64(img_a_inicio)
    img_af_b64, img_af_type = file_to_base64(img_a_final)
    img_bi_b64, img_bi_type = file_to_base64(img_b_inicio)
    img_bf_b64, img_bf_type = file_to_base64(img_b_final)

    result, tiempo = analyze_video(
        str(path),
        "video/mp4",
        robot_a,
        robot_b,
        img_ai_b64,
        img_ai_type,
        img_af_b64,
        img_af_type,
        img_bi_b64,
        img_bi_type,
        img_bf_b64,
        img_bf_type,
    )

    if result is None:
        return templates.TemplateResponse(
            request,
            "index.html",
            {
                "request": request,
                "error": "Error al procesar el video con Gemini",
            },
        )

    if isinstance(result, dict) and "error" in result:
        return templates.TemplateResponse(
            request,
            "index.html",
            {
                "request": request,
                "error": str(result),
            },
        )

    try:
        texto = result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return templates.TemplateResponse(
            request,
            "index.html",
            {
                "request": request,
                "error": "Respuesta inválida de Gemini",
            },
        )

    parsed = parse_result(texto, robot_a, robot_b)
    ganador = parsed.get("ganador", "No definido")

    try:
        save_analysis(filename, robot_a, robot_b, ganador, tiempo)
    except Exception as e:
        print(f"Error guardando en BD: {e}")

    LAST_VIDEO_NAME = None
    LAST_VIDEO_TIME = None

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "request": request,
            "ganador": ganador,
            "response": texto,
            "tiempo": tiempo,
        },
    )


@router.get("/historial")
def historial():
    try:
        return get_historial()
    except Exception as e:
        return [
            {
                "robot_a": "-",
                "robot_b": "-",
                "ganador": f"Error BD: {e}",
                "tiempo": "-",
            }
        ]