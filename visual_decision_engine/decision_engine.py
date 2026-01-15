import json

SEGMENTS_PATH = "../segmentation/segments.json"
CAPTIONS_PATH = "../caption_engine/captions.json"
OUTPUT_PATH = "visual_decisions.json"

TITLE_PAUSE_THRESHOLD = 1.2
LONG_SEGMENT_THRESHOLD = 6
EMPHASIS_WORD_THRESHOLD = 2

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_visual_decisions(segments):
    decisions = []

    for i, segment in enumerate(segments):
        segment_duration = segment["end"] - segment["start"]
        emphasized_words = [
            w for w in segment["words"] if w.get("emphasized")
        ]

        add_title = False
        add_emphasis = False
        add_overlay = False

        if i == 0:
            add_title = True
        elif segment["start"] - segments[i-1]["end"] >= TITLE_PAUSE_THRESHOLD:
            add_title = True

        if len(emphasized_words) >= EMPHASIS_WORD_THRESHOLD:
            add_emphasis = True
        if segment_duration >= 5:
            add_emphasis = True

        if segment_duration >= LONG_SEGMENT_THRESHOLD:
            add_overlay = True

        decisions.append({
            "segment_index": i,
            "start": segment["start"],
            "end": segment["end"],
            "title": add_title,
            "emphasis": add_emphasis,
            "overlay": add_overlay,
            "reasoning": {
                "long_pause": i > 0 and segment["start"] - segments[i-1]["end"] >= TITLE_PAUSE_THRESHOLD,
                "emphasized_words": len(emphasized_words),
                "segment_duration": round(segment_duration, 2)
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
