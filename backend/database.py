import psycopg2
from config import *

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

# 🔹 GUARDAR ANALISIS
def save_analysis(video, robot_a, robot_b, ganador, tiempo):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO analisis (nombre_video, robot_a, robot_b, resultado, tiempo_procesamiento)
    VALUES (%s, %s, %s, %s, %s)
    """

    cursor.execute(query, (video, robot_a, robot_b, ganador, tiempo))

    conn.commit()
    cursor.close()
    conn.close()


# 🔹 OBTENER HISTORIAL
def get_historial():
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT robot_a, robot_b, resultado, tiempo_procesamiento
    FROM analisis
    ORDER BY id DESC
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    historial = []
    for r in rows:
        historial.append({
            "robot_a": r[0],
            "robot_b": r[1],
            "ganador": r[2],
            "tiempo": r[3]
        })

    return historial