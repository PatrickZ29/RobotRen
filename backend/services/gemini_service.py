import base64
import requests
import time

from api_keys import get_api_key
from services.prompt_service import crear_prompt


def analyze_video(
    video_path, mime, robot_a, robot_b,
    img_ai_b64=None, img_ai_type=None,
    img_af_b64=None, img_af_type=None,
    img_bi_b64=None, img_bi_type=None,
    img_bf_b64=None, img_bf_type=None
):
    with open(video_path, "rb") as f:
        video_base64 = base64.b64encode(f.read()).decode()

    parts = []

    # ── BLOQUE 1: imágenes de referencia ANTES del prompt ──
    # Gemini las ancla en memoria antes de recibir instrucciones.
    def add_image(label, b64, mime_type):
        if b64:
            parts.append({"text": label})
            parts.append({
                "inline_data": {
                    "mime_type": mime_type,
                    "data": b64
                }
            })

    add_image(
        f"REFERENCIA_A_INICIO: Esta es la foto de {robot_a} antes del combate. "
        f"Memoriza su apariencia exacta: color, forma, arma y cualquier detalle único.",
        img_ai_b64, img_ai_type
    )
    add_image(
        f"REFERENCIA_B_INICIO: Esta es la foto de {robot_b} antes del combate. "
        f"Memoriza su apariencia exacta: color, forma, arma y cualquier detalle único.",
        img_bi_b64, img_bi_type
    )

    
    parts.append({"text": crear_prompt(robot_a, robot_b)})

    
    parts.append({
        "inline_data": {
            "mime_type": mime,
            "data": video_base64
        }
    })


    add_image(
        f"REFERENCIA_A_FINAL: Estado de {robot_a} al terminar el combate. "
        f"Úsala para evaluar Condición en el Criterio 2.",
        img_af_b64, img_af_type
    )
    add_image(
        f"REFERENCIA_B_FINAL: Estado de {robot_b} al terminar el combate. "
        f"Úsala para evaluar Condición en el Criterio 2.",
        img_bf_b64, img_bf_type
    )

    api_key = get_api_key()
    model = "gemini-3.1-flash-lite"  

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        f"models/{model}:generateContent?key={api_key}"
    )

    data = {
        "contents": [
            {
                "parts": parts
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "topP": 0.8,
            "topK": 40
        }
    }

    inicio = time.time()

    try:
        response = requests.post(url, json=data, timeout=300)
        response.raise_for_status()
        res_json = response.json()
    except Exception as e:
        return {"error": str(e)}, 0

    tiempo = round(time.time() - inicio, 2)
    return res_json, tiempo