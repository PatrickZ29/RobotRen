import psycopg2
from config import DATABASE_URL, DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD


def get_connection():
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)

    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS analisis (
            id SERIAL PRIMARY KEY,
            nombre_video TEXT,
            robot_a TEXT NOT NULL,
            robot_b TEXT NOT NULL,
            resultado TEXT NOT NULL,
            tiempo_procesamiento NUMERIC,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    conn.commit()
    cursor.close()
    conn.close()


def save_analysis(video, robot_a, robot_b, ganador, tiempo):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO analisis (
            nombre_video,
            robot_a,
            robot_b,
            resultado,
            tiempo_procesamiento
        )
        VALUES (%s, %s, %s, %s, %s);
        """,
        (video, robot_a, robot_b, ganador, tiempo),
    )

    conn.commit()
    cursor.close()
    conn.close()


def get_historial():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT robot_a, robot_b, resultado, tiempo_procesamiento, fecha
        FROM analisis
        ORDER BY id DESC
        LIMIT 50;
        """
    )

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    historial = []

    for row in rows:
        historial.append(
            {
                "robot_a": row[0],
                "robot_b": row[1],
                "ganador": row[2],
                "tiempo": float(row[3]) if row[3] is not None else None,
                "fecha": row[4].strftime("%Y-%m-%d %H:%M:%S") if row[4] else None,
            }
        )

    return historial