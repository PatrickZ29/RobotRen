import os
from dotenv import load_dotenv

load_dotenv()


def get_api_key():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise Exception("GEMINI_API_KEY no configurada en variables de entorno")
    return api_key
