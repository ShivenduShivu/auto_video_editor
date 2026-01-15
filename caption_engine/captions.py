import json
import math

INPUT_PATH = "../segmentation/segments.json"
OUTPUT_PATH = "captions.json"

MAX_WORDS_PER_CAPTION = 7

def load_segments():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_captions(segments):
    captions = []

    for seg_idx, segment in enumerate(segments):
        words = segment["words"]
        segment_start = segment["start"]
        segment_end = segment["end"]

        total_words = len(words)
        chunks = math.ceil(total_words / MAX_WORDS_PER_CAPTION)

        for i in range(chunks):
            chunk_words = words[i*MAX_WORDS_PER_CAPTION:(i+1)*MAX_WORDS_PER_CAPTION]

            caption_text = " ".join([w["word"] for w in chunk_words])

            emphasized_words = [
                w["word"] for w in chunk_words if w.get("emphasized")
            ]

            animation = "fade"
            if i == 0:
                animation = "fade_in"
            if emphasized_words:
                animation = "pop"

            captions.append({
                "start": chunk_words[0]["start"],
                "end": chunk_words[-1]["end"],
                "text": caption_text,
                "highlight": emphasized_words,
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
