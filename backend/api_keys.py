API_KEY = "AIzaSyBrIrK1bpY2alTYpR5txB1uJLt3f7"

def get_api_key():
    if not API_KEY:
        raise Exception("API KEY no configurada")
    return API_KEY