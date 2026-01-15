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

def generate_captions(segments):
    captions = []

    for segment in segments:
        words = segment["words"]
        chunks = math.ceil(len(words) / MAX_WORDS_PER_CAPTION)

        for i in range(chunks):
            chunk = words[i*MAX_WORDS_PER_CAPTION:(i+1)*MAX_WORDS_PER_CAPTION]

            text = " ".join(w["word"] for w in chunk)
            highlights = [w["word"] for w in chunk if w.get("emphasized")]

            animation = "fade"
            if i == 0:
                animation = "fade_in"
            if highlights:
                animation = "pop"

            captions.append({
                "start": chunk[0]["start"],
                "end": chunk[-1]["end"],
                "text": text,
                "highlight": highlights,
                "animation": animation
            })

    return captions

def main():
    segments = load_segments()
    captions = generate_captions(segments)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(captions, f, indent=2)

    print(f"✅ Caption engine complete — {len(captions)} captions generated")

if __name__ == "__main__":
    main()
