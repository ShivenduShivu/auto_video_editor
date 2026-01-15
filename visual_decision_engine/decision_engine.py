import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SEGMENTS_PATH = os.path.join(BASE_DIR, "../segmentation/segments.json")
OUTPUT_PATH = os.path.join(BASE_DIR, "visual_decisions.json")

TITLE_PAUSE_THRESHOLD = 1.2
LONG_SEGMENT_THRESHOLD = 6
EMPHASIS_WORD_THRESHOLD = 2

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_visual_decisions(segments):
    decisions = []

    for i, segment in enumerate(segments):
        duration = segment["end"] - segment["start"]
        emphasized = [w for w in segment["words"] if w.get("emphasized")]

        decisions.append({
            "segment_index": i,
            "start": segment["start"],
            "end": segment["end"],
            "title": i == 0,
            "emphasis": len(emphasized) >= EMPHASIS_WORD_THRESHOLD or duration >= 5,
            "overlay": duration >= LONG_SEGMENT_THRESHOLD,
            "reasoning": {
                "emphasized_words": len(emphasized),
                "segment_duration": round(duration, 2)
            }
        })

    return decisions

def main():
    segments = load_json(SEGMENTS_PATH)
    decisions = generate_visual_decisions(segments)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(decisions, f, indent=2)

    print("✅ Visual decision engine complete")

if __name__ == "__main__":
    main()
