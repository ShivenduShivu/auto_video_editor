import json
import os
from collections import Counter

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SEGMENTS_PATH = os.path.join(BASE_DIR, "segmentation", "segments.json")
CAPTIONS_PATH = os.path.join(BASE_DIR, "caption_engine", "captions.json")
OUTPUT_PATH = os.path.join(BASE_DIR, "visual_decisions.json")

# -----------------------------
# TOPIC KEYWORDS (EXTENSIBLE)
# -----------------------------

TOPIC_KEYWORDS = {
    "ai": [
        "ai", "artificial", "intelligence", "model",
        "machine", "learning", "neural", "llm"
    ],
    "education": [
        "learn", "learning", "student", "students",
        "teacher", "course", "education", "class"
    ],
    "business": [
        "startup", "business", "market", "growth",
        "revenue", "customer", "company", "product"
    ]
}

# -----------------------------
# HELPERS
# -----------------------------

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def infer_topic(words):
    counter = Counter()

    for word in words:
        w = word.lower()
        for topic, keywords in TOPIC_KEYWORDS.items():
            if w in keywords:
                counter[topic] += 1

    if not counter:
        return "generic"

    return counter.most_common(1)[0][0]

# -----------------------------
# MAIN LOGIC
# -----------------------------

def main():
    segments = load_json(SEGMENTS_PATH)
    captions = load_json(CAPTIONS_PATH)

    visual_decisions = []

    # IMPORTANT: segment_index is derived by enumerate
    for seg_index, seg in enumerate(segments):
        seg_start = seg["start"]
        seg_end = seg["end"]

        seg_words = []

        for cap in captions:
            if cap["start"] >= seg_start and cap["end"] <= seg_end:
                for w in cap.get("words", []):
                    seg_words.append(w.get("word") or w.get("text", ""))

        topic = infer_topic(seg_words)

        visual_decisions.append({
            "segment_index": seg_index,
            "start": seg_start,
            "end": seg_end,
            "title": seg_index == 0,
            "emphasis": True,
            "overlay": True,
            "topic": topic
        })

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(visual_decisions, f, indent=2)

    print("✅ Visual decision engine complete (segment-level topic inference enabled)")

if __name__ == "__main__":
    main()
