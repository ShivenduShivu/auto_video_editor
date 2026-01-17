import json
import os
from deep_translator import GoogleTranslator

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CAPTIONS_DIR = os.path.join(PROJECT_ROOT, "caption_engine")
STATE_PATH = os.path.join(PROJECT_ROOT, "nlp_command_parser", "editor_state.json")

SOURCE_CAPTIONS = os.path.join(CAPTIONS_DIR, "captions.json")

LANGUAGE_MAP = {
    "en": "en",
    "hi": "hi",
    "te": "te"
}

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    state = load_json(STATE_PATH)
    lang = state.get("captions", {}).get("language", "original")

    if lang == "original":
        print("ℹ️ Original language selected. Skipping translation.")
        return

    if lang not in LANGUAGE_MAP:
        print(f"❌ Unsupported language: {lang}")
        return

    out_path = os.path.join(CAPTIONS_DIR, f"captions_{lang}.json")
    if os.path.exists(out_path):
        print("ℹ️ Translated captions already exist.")
        return

    captions = load_json(SOURCE_CAPTIONS)
    translator = GoogleTranslator(source="auto", target=LANGUAGE_MAP[lang])

    print(f"🌍 Translating captions to {lang.upper()} (deep-translator)")

    for segment in captions:
        words = segment["words"]
        sentence = " ".join(w["text"] for w in words)

        translated = translator.translate(sentence)
        translated_words = translated.split()

        for i, word in enumerate(words):
            word["text"] = translated_words[i] if i < len(translated_words) else ""

    save_json(out_path, captions)
    print(f"✅ Saved {out_path}")

if __name__ == "__main__":
    main()
