import subprocess
import os

INPUT_VIDEO = "../input_video/raw.mp4"
OUTPUT_AUDIO = "audio.wav"

def extract_audio():
    if not os.path.exists(INPUT_VIDEO):
        raise FileNotFoundError("Input video not found")

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
