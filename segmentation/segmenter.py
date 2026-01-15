import json
from statistics import mean

INPUT_PATH = "../transcription/transcript.json"
OUTPUT_PATH = "segments.json"

PAUSE_THRESHOLD = 0.7      # seconds
MAX_SEGMENT_DURATION = 7  # seconds

STRONG_KEYWORDS = {
    "important", "key", "critical", "remember",
    "main", "focus", "note"
}

def load_words():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def detect_segments(words):
    segments = []
    current_segment = []
    segment_start_time = words[0]["start"]

    durations = [(w["end"] - w["start"]) for w in words]
    avg_duration = mean(durations)

    for i, word in enumerate(words):
        emphasized = False
        duration = word["end"] - word["start"]

        if duration > 1.3 * avg_duration:
            emphasized = True
        if word["word"].isupper():
            emphasized = True
        if word["word"].lower() in STRONG_KEYWORDS:
            emphasized = True

        word["emphasized"] = emphasized

        current_segment.append(word)

        is_last = i == len(words) - 1
        if not is_last:
            pause = words[i + 1]["start"] - word["end"]
            segment_duration = word["end"] - segment_start_time

            if (
                pause >= PAUSE_THRESHOLD or
                word["word"].endswith((".", "?", "!")) or
                segment_duration >= MAX_SEGMENT_DURATION
            ):
                segments.append({
                    "start": segment_start_time,
                    "end": word["end"],
                    "words": current_segment
                })
                current_segment = []
                segment_start_time = words[i + 1]["start"]

    if current_segment:
        segments.append({
            "start": segment_start_time,
            "end": current_segment[-1]["end"],
            "words": current_segment
        })

    return segments

def main():
    words = load_words()
    segments = detect_segments(words)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(segments, f, indent=2)

    print(f"✅ Segmentation complete — {len(segments)} segments created")

if __name__ == "__main__":
    main()
