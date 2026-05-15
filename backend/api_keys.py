API_KEY = "-CUH3Pe1le04x8iianL75GcJKs4ATwBM"

def get_api_key():
    if not API_KEY:
        raise Exception("API KEY no configurada")
    return API_KEY