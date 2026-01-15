import whisper
import json

AUDIO_PATH = "../audio_processing/audio.wav"
OUTPUT_JSON = "transcript.json"

def transcribe():
    model = whisper.load_model("base")

    result = model.transcribe(
        AUDIO_PATH,
        word_timestamps=True,
        verbose=False
    )

    transcript = []

    for segment in result["segments"]:
        for word in segment["words"]:
            transcript.append({
                "word": word["word"].strip(),
                "start": round(word["start"], 3),
                "end": round(word["end"], 3)
            })

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(transcript, f, indent=2)

    print("✅ Transcription complete")

if __name__ == "__main__":
    transcribe()
