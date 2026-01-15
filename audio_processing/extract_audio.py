import subprocess
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_VIDEO = os.path.join(BASE_DIR, "../input_video/raw.mp4")
OUTPUT_AUDIO = os.path.join(BASE_DIR, "audio.wav")

def extract_audio():
    if not os.path.exists(INPUT_VIDEO):
        raise FileNotFoundError(f"Input video not found at {INPUT_VIDEO}")

    command = [
        "ffmpeg",
        "-y",
        "-i", INPUT_VIDEO,
        "-ac", "1",
        "-ar", "16000",
        OUTPUT_AUDIO
    ]

    subprocess.run(command, check=True)
    print("✅ Audio extracted successfully")

if __name__ == "__main__":
    extract_audio()
