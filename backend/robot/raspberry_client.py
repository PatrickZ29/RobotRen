import requests
import time
import subprocess
import signal
import os
from datetime import datetime


# SERVIDORES DISPONIBLES
SERVERS = [
    "http://172.19.17.39:8000",
    "http://172.20.10.12:8000"
]


# CONFIGURACIÓN DE VIDEO
WIDTH = 1280
HEIGHT = 720
FPS = 24
CRF = 28
DEVICE = "/dev/video0"


# VARIABLES DE CONTROL

recording = False
paused = False
filename = None
current_segment = None
segment_files = []



# OBTENER SERVIDOR ACTIVO

def get_active_server():
    for server in SERVERS:
        try:
            response = requests.get(
                f"{server}/recording_status",
                timeout=2
            )
            if response.status_code == 200:
                return server
        except Exception:
            continue
    return None

# INICIAR UN SEGMENTO DE VIDEO

def start_segment():
    global current_segment

    segment_name = f"segment_{len(segment_files):03d}.mp4"
    segment_files.append(segment_name)
    current_segment = segment_name

    print(f"Grabando segmento: {segment_name}")

    process = subprocess.Popen([
        "ffmpeg",
        "-f", "v4l2",
        "-input_format", "yuyv422",
        "-video_size", f"{WIDTH}x{HEIGHT}",
        "-framerate", str(FPS),
        "-i", DEVICE,

        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", str(CRF),
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",

        "-an",
        "-y",
        segment_name
    ])

    return process


# INICIAR GRABACIÓN
def start_recording():
    global recording, paused, filename, segment_files, process

    if recording:
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"video_{timestamp}.mp4"

    segment_files = []
    paused = False
    recording = True

    process = start_segment()



# PAUSAR GRABACIÓN
def pause_recording():
    global paused, process

    if not recording or paused or process is None:
        return

    print("Grabación pausada")

    process.send_signal(signal.SIGINT)
    process.wait()

    process = None
    paused = True


# REANUDAR GRABACIÓN
def resume_recording():
    global paused, process

    if not recording or not paused:
        return

    print("Grabación reanudada")

    process = start_segment()
    paused = False



# UNIR SEGMENTOS

def merge_segments():
    global filename

    if not segment_files:
        return None

    # Si solo existe un segmento
    if len(segment_files) == 1:
        os.rename(segment_files[0], filename)
        return filename

    # Crear lista para ffmpeg concat
    with open("segments.txt", "w") as f:
        for seg in segment_files:
            f.write(f"file '{seg}'\n")

    print("Uniendo segmentos...")

    subprocess.run([
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", "segments.txt",
        "-c", "copy",
        "-y",
        filename
    ])

    # Eliminar segmentos temporales
    for seg in segment_files:
        if os.path.exists(seg):
            os.remove(seg)

    if os.path.exists("segments.txt"):
        os.remove("segments.txt")

    return filename


# SUBIR VIDEO
def upload_video(server):
    global filename

    if not filename or not os.path.exists(filename):
        print("No se encontró el archivo final")
        return

    size_mb = os.path.getsize(filename) / (1024 * 1024)
    print(f"Tamaño del video: {size_mb:.2f} MB")

    if size_mb < 0.01:
        print("Video inválido")
        return

    print("Enviando video...")

    try:
        with open(filename, "rb") as f:
            response = requests.post(
                f"{server}/upload",
                files={"video": (filename, f, "video/mp4")},
                timeout=300
            )

        if response.status_code == 200:
            print("Video enviado correctamente")
            os.remove(filename)
            print("Archivo local eliminado")
        else:
            print("Error al subir:", response.text)

    except Exception as e:
        print("Error al enviar video:", e)


# DETENER GRABACIÓN
def stop_recording(server):
    global recording, paused, process

    if not recording:
        return

    print("Deteniendo grabación...")

    if process:
        process.send_signal(signal.SIGINT)
        process.wait()
        process = None

    recording = False
    paused = False

    merge_segments()
    time.sleep(2)
    upload_video(server)


# LOOP PRINCIPAL
print("Sistema de grabación iniciado")

process = None

while True:
    try:
        server = get_active_server()

        if not server:
            print("No hay servidor disponible")
            time.sleep(5)
            continue

        response = requests.get(
            f"{server}/recording_status",
            timeout=2
        )

        if response.status_code != 200:
            time.sleep(1)
            continue

        data = response.json()

        server_recording = data.get("recording", False)
        server_paused = data.get("paused", False)

        print(
            f"Servidor -> recording={server_recording}, paused={server_paused} | "
            f"Local -> recording={recording}, paused={paused}"
        )

        # Iniciar
        if server_recording and not recording:
            start_recording()

        # Pausar
        elif (
            server_recording
            and server_paused
            and recording
            and not paused
        ):
            pause_recording()

        # Reanudar
        elif (
            server_recording
            and not server_paused
            and recording
            and paused
        ):
            resume_recording()

        # Detener
        elif not server_recording and recording:
            stop_recording(server)

        time.sleep(1)

    except Exception as e:
        print("Error:", e)
        time.sleep(3)