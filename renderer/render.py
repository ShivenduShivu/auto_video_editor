import os
import json
import subprocess
from moviepy.editor import (
    VideoFileClip,
    CompositeVideoClip,
    TextClip,
    ImageClip
)
from PIL import Image, ImageDraw, ImageFont
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

VIDEO_PATH = os.path.join(PROJECT_ROOT, "input_video", "raw.mp4")
CAPTIONS_DIR = os.path.join(PROJECT_ROOT, "caption_engine")
STATE_PATH = os.path.join(PROJECT_ROOT, "nlp_command_parser", "editor_state.json")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "renderer", "output.mp4")
BASE_OUTPUT_PATH = os.path.join(PROJECT_ROOT, "renderer", "base.mp4")

FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def ensure_translated_captions():
    state = load_json(STATE_PATH)
    lang = state.get("captions", {}).get("language", "original")

    if lang == "original":
        return os.path.join(CAPTIONS_DIR, "captions.json")

    translated = os.path.join(CAPTIONS_DIR, f"captions_{lang}.json")
    if not os.path.exists(translated):
        subprocess.run(
            ["python", "translation/translate_captions.py"],
            cwd=PROJECT_ROOT,
            check=True
        )
    return translated


# ---------- ENGLISH (PIL, word-level, kinetic) ----------
def render_caption_image(words, width, bold):
    img = Image.new("RGBA", (width, 120), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    font_path = FONT_BOLD if bold else FONT_REGULAR
    font = ImageFont.truetype(font_path, 40)

    x = 20
    y = 40
    for w in words:
        color = (255, 215, 0, 255) if w.get("emphasis") else (255, 255, 255, 255)
        draw.text((x, y), w["text"] + " ", font=font, fill=color)
        x += int(font.getlength(w["text"] + " "))

    return img


# ---------- HINDI / TELUGU (TextClip, sentence-level) ----------
def render_sentence_clip(text, start, end, video_w, video_h):
    return (
        TextClip(
            text,
            fontsize=48,
            color="white",
            method="pango",   # required for Indic scripts
            size=(int(video_w * 0.9), None),
            align="center"
        )
        .set_position(("center", video_h - 140))
        .set_start(start)
        .set_end(end)
    )


def main():
    state = load_json(STATE_PATH)
    captions_path = ensure_translated_captions()
    captions = load_json(captions_path)

    video = VideoFileClip(VIDEO_PATH)

    # Base render (no captions)
    video.write_videofile(BASE_OUTPUT_PATH, codec="libx264", audio_codec="aac")
    print(f"✅ Base video rendered: {BASE_OUTPUT_PATH}")

    lang = state.get("captions", {}).get("language", "original")
    overlays = []

    for seg in captions:
        start = seg["start"]
        end = seg["end"]

        if lang in ["hi", "te"]:
            sentence = " ".join(w["text"] for w in seg["words"])
            clip = render_sentence_clip(sentence, start, end, video.w, video.h)
            overlays.append(clip)
        else:
            img = render_caption_image(
                seg["words"],
                video.w,
                state["caption_style"].get("bold", False)
            )

            clip = (
                ImageClip(np.array(img), ismask=False)
                .set_start(start)
                .set_end(end)
                .set_position(("center", video.h - 140))
            )
            overlays.append(clip)

    final = CompositeVideoClip([video] + overlays)
    final.write_videofile(OUTPUT_PATH, codec="libx264", audio_codec="aac")

    print(f"✅ Final video rendered with captions: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
