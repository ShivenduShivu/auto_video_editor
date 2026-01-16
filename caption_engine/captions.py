import os
import json
import math

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_PATH = os.path.join(BASE_DIR, "../segmentation/segments.json")
OUTPUT_PATH = os.path.join(BASE_DIR, "captions.json")

MAX_WORDS_PER_CAPTION = 7

def load_segments():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def segment_context(idx, total):
    if idx == 0:
        return "intro"
    if idx == total - 1:
        return "conclusion"
    return "body"

def generate_captions(segments):
    captions = []
    total_segments = len(segments)

    for seg_idx, segment in enumerate(segments):
        words = segment["words"]
        context = segment_context(seg_idx, total_segments)

        chunks = math.ceil(len(words) / MAX_WORDS_PER_CAPTION)

        for i in range(chunks):
            chunk = words[i*MAX_WORDS_PER_CAPTION:(i+1)*MAX_WORDS_PER_CAPTION]

            word_items = []
            for w in chunk:
                word_items.append({
                    "text": w["word"],
                    "emphasis": bool(w.get("emphasized", False)),
                    "context": context
                })

            captions.append({
                "start": chunk[0]["start"],
                "end": chunk[-1]["end"],
                "words": word_items
            })

    return captions

def main():
    segments = load_segments()
    captions = generate_captions(segments)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(captions, f, indent=2)

    print(f"✅ Caption engine upgraded — {len(captions)} word-level captions generated")

if __name__ == "__main__":
    main()
