API_KEY = "AIzaSyB61LaPzOLysBap-oTc0PWKlUOxQZtKS5U"

def get_api_key():
    if not API_KEY:
        raise Exception("API KEY no configurada")
    return API_KEY