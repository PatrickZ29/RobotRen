API_KEY = "AIzaSyAgLTc3w9ukS2DfIT1iaJnm0ZoMJ-9XnMc"

def get_api_key():
    if not API_KEY:
        raise Exception("API KEY no configurada")
    return API_KEY