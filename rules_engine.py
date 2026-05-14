import json

def procesar_resultado(respuesta_modelo):

    try:
        data = json.loads(respuesta_modelo)
        return data
    except:
        return {
            "error": "La respuesta del modelo no es JSON válido",
            "raw_response": respuesta_modelo
        }