import json
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CAPTION_DIR = os.path.join(PROJECT_ROOT, "caption_engine")
SEGMENTS_PATH = os.path.join(PROJECT_ROOT, "segmentation", "segments.json")
OUTPUT_PATH = os.path.join(CAPTION_DIR, "captions.json")


def clear_old_translations():
    """
    Hackathon-safe cache invalidation:
    Remove translated captions whenever a new video is processed.
    """
    for fname in os.listdir(CAPTION_DIR):
        if fname.startswith("captions_") and fname != "captions.json":
            path = os.path.join(CAPTION_DIR, fname)
            os.remove(path)
            print(f"🧹 Removed stale translated captions: {fname}")


def main():
    # 🔑 CRITICAL FIX: clear old translated captions
    clear_old_translations()

    with open(SEGMENTS_PATH, "r", encoding="utf-8") as f:
        segments = json.load(f)

    captions = []
    for seg in segments:
        captions.append({
            "start": seg["start"],
            "end": seg["end"],
            "words": seg["words"]
        })

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(captions, f, indent=2, ensure_ascii=False)

    print(f"✅ Caption engine complete — {len(captions)} segments written")


if __name__ == "__main__":
    main()
