API_KEY = "AIzaSyABbri8O_8IDENni5qHZxImoC_CFCHsIoY"

def get_api_key():
    if not API_KEY:
        raise Exception("API KEY no configurada")
    return API_KEY