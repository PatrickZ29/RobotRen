API_KEY = "AIzaSyBXpwJMtz0hvvzihoKBSqa9yIKw4re3P5g"

def get_api_key():
    if not API_KEY:
        raise Exception("API KEY no configurada")
    return API_KEY