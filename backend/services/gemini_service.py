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

    # Leer y convertir el video a Base64
    with open(video_path, "rb") as f:
        video_base64 = base64.b64encode(f.read()).decode()

    # Partes del prompt
    parts = [
        {"text": crear_prompt(robot_a, robot_b)},
        {
            "inline_data": {
                "mime_type": mime,
                "data": video_base64
            }
        }
    ]

    # Función para agregar imágenes opcionales
    def add_image(label, b64, mime_type):
        if b64:
            parts.append({"text": label})
            parts.append({
                "inline_data": {
                    "mime_type": mime_type,
                    "data": b64
                }
            })

    # Agregar imágenes si existen
    add_image("Imagen inicial Robot A", img_ai_b64, img_ai_type)
    add_image("Imagen final Robot A", img_af_b64, img_af_type)
    add_image("Imagen inicial Robot B", img_bi_b64, img_bi_type)
    add_image("Imagen final Robot B", img_bf_b64, img_bf_type)

    # API Key
    api_key = get_api_key()

    # Modelo Gemini 3.1 Flash Lite
    model = "gemini-3.1-flash-lite"

    # URL de la API
    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        f"models/{model}:generateContent?key={api_key}"
    )

    # Datos de la solicitud
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

    # Medir tiempo de respuesta
    inicio = time.time()

    try:
        response = requests.post(url, json=data, timeout=300)
        response.raise_for_status()
        res_json = response.json()
    except Exception as e:
        return {"error": str(e)}, 0

    tiempo = round(time.time() - inicio, 2)

    return res_json, tiempo