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

    parts = [
        {"text": crear_prompt(robot_a, robot_b)},
        {
            "inline_data": {
                "mime_type": mime,
                "data": video_base64
            }
        }
    ]

    def add_image(label, b64, mime):
        if b64:
            parts.append({"text": label})
            parts.append({
                "inline_data": {
                    "mime_type": mime,
                    "data": b64
                }
            })

    add_image("Imagen inicial Robot A", img_ai_b64, img_ai_type)
    add_image("Imagen final Robot A", img_af_b64, img_af_type)
    add_image("Imagen inicial Robot B", img_bi_b64, img_bi_type)
    add_image("Imagen final Robot B", img_bf_b64, img_bf_type)

    api_key = get_api_key()

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

    data = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "temperature": 0.2,
            "topP": 0.8,
            "topK": 40
        }
    }

    inicio = time.time()

    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        res_json = response.json()
    except Exception as e:
        return {"error": str(e)}, 0

    tiempo = round(time.time() - inicio, 2)

    return res_json, tiempo