import re

def parse_result(texto, robot_a, robot_b):

    if not texto:
        return {"error": "Respuesta vacía"}

    try:
        # 🔥 Escapar nombres por seguridad
        robot_a_esc = re.escape(robot_a)
        robot_b_esc = re.escape(robot_b)

        def buscar(patron):
            m = re.search(patron, texto, re.IGNORECASE | re.DOTALL)
            return m.group(1).strip() if m else "-"

        # 🔥 GANADOR más robusto
        ganador = buscar(r"GANADOR\s*:\s*([A-Za-z0-9_ ]+)")

        # 🔥 Función para cada robot
        def parse_robot(nombre_esc):
            return {
                "agresividad": buscar(rf"{nombre_esc}.*?Agresividad\s*:\s*(\d+)"),
                "condicion": buscar(rf"{nombre_esc}.*?Condición\s*:\s*(\d+)"),
                "danio": buscar(rf"{nombre_esc}.*?Daño\s*:\s*(\d+)"),
                "control": buscar(rf"{nombre_esc}.*?Control\s*:\s*(\d+)"),
                "total": buscar(rf"{nombre_esc}.*?TOTAL\s*:\s*(\d+)")
            }

        return {
            "ganador": ganador,
            "robot_a": parse_robot(robot_a_esc),
            "robot_b": parse_robot(robot_b_esc)
        }

    except Exception as e:
        return {"error": str(e)}