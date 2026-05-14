import os
from config import VIDEO_FOLDER

os.makedirs(VIDEO_FOLDER, exist_ok=True)


def save_video(filename, video_bytes):

    path = f"{VIDEO_FOLDER}/{filename}"

    with open(path, "wb") as f:
        f.write(video_bytes)

    return path