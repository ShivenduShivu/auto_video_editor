import os
import json
import subprocess
import sys
from moviepy.editor import (
    VideoFileClip,
    CompositeVideoClip,
    ImageClip
)
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# -------------------- PATHS --------------------

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

VIDEO_PATH = os.path.join(PROJECT_ROOT, "input_video", "raw.mp4")
CAPTIONS_DIR = os.path.join(PROJECT_ROOT, "caption_engine")
DECISIONS_PATH = os.path.join(
    PROJECT_ROOT,
    "visual_decision_engine",
    "visual_decisions.json"
)

STATE_PATH = os.path.join(PROJECT_ROOT, "nlp_command_parser", "editor_state.json")

BASE_OUTPUT_PATH = os.path.join(PROJECT_ROOT, "renderer", "base.mp4")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "renderer", "output.mp4")

FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# -------------------- UTILS --------------------

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
            [sys.executable, "translation/translate_captions.py"],
            cwd=PROJECT_ROOT,
            check=True
        )
    return translated

# -------------------- VISUAL PRESETS --------------------
# Odysser-style: calm, consistent, explainable

COLORS = {
    "text": (255, 255, 255, 255),
    "accent": (255, 200, 0, 255),
    "bg": (20, 20, 20, 180)
}

FONT_SIZES = {
    "normal": 40,
    "title": 56
}

PADDING = 24
RADIUS = 16

# -------------------- RENDER HELPERS --------------------

def draw_rounded_rect(draw, box, radius, fill):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=fill)

def render_caption_block(words, width, style):
    """
    Renders captions with safe max-2-line wrapping.
    Odysser-style: calm, readable, never overflowing.
    """

    font_size = FONT_SIZES["title"] if style == "title" else FONT_SIZES["normal"]
    font_path = FONT_BOLD if style in ["title", "emphasis"] else FONT_REGULAR
    font = ImageFont.truetype(font_path, font_size)

    max_text_width = width - 160  # hard safety margin

    # ---- STEP 1: word-wise line wrapping (max 2 lines) ----
    lines = []
    current_line = []
    dummy_img = Image.new("RGBA", (10, 10))
    d = ImageDraw.Draw(dummy_img)

    for w in words:
        text = w.get("text") or w.get("word")
        if not text:
            continue

        test_line = current_line + [text]
        test_text = " ".join(test_line)
        test_width = d.textlength(test_text, font=font)

        if test_width <= max_text_width:
            current_line.append(text)
        else:
            lines.append(current_line)
            current_line = [text]

        if len(lines) == 2:
            break

    if current_line and len(lines) < 2:
        lines.append(current_line)

    # ---- STEP 2: calculate image size ----
    line_height = font_size + 8
    text_block_height = len(lines) * line_height
    img_w = max(
        int(d.textlength(" ".join(line), font=font)) for line in lines
    ) + PADDING * 2
    img_h = text_block_height + PADDING * 2

    img = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # ---- STEP 3: background block if needed ----
    if style in ["title", "overlay"]:
        draw_rounded_rect(
            draw,
            (0, 0, img_w, img_h),
            RADIUS,
            COLORS["bg"]
        )

    # ---- STEP 4: draw text centered ----
    y = PADDING
    for line_words in lines:
        line_text = " ".join(line_words)
        line_width = int(d.textlength(line_text, font=font))

        # Center this line independently
        x = (img_w - line_width) // 2

        for word in line_words:
            color = COLORS["accent"] if any(
                w.get("word") == word and w.get("emphasized") for w in words
            ) else COLORS["text"]

            draw.text((x, y), word + " ", font=font, fill=color)
            x += int(font.getlength(word + " "))

        y += line_height

    return img


# -------------------- MAIN --------------------

def main():
    captions_path = ensure_translated_captions()
    captions = load_json(captions_path)
    decisions = load_json(DECISIONS_PATH)

    decision_map = {d["segment_index"]: d for d in decisions}

    video = VideoFileClip(VIDEO_PATH)

    # Base render
    video.write_videofile(BASE_OUTPUT_PATH, codec="libx264", audio_codec="aac")

    overlays = []

    for i, seg in enumerate(captions):
        decision = decision_map.get(i, {})
        style = "normal"

        if decision.get("title"):
            style = "title"
        elif decision.get("overlay"):
            style = "overlay"
        elif decision.get("emphasis"):
            style = "emphasis"

        img = render_caption_block(seg["words"], video.w, style)

        # Positioning (Odysser-like hierarchy)
        if style == "title":
            pos = ("center", video.h * 0.25)
        elif style == "overlay":
            pos = ("center", video.h * 0.78)
        else:
            pos = ("center", video.h * 0.82)

        clip = (
            ImageClip(np.array(img))
            .set_start(seg["start"])
            .set_end(seg["end"])
            .set_position(pos)
            .fadein(0.2)
            .fadeout(0.2)
        )

        overlays.append(clip)

    final = CompositeVideoClip([video] + overlays)
    final.write_videofile(OUTPUT_PATH, codec="libx264", audio_codec="aac")

    print("✅ Final video rendered with Odysser-style visuals")

if __name__ == "__main__":
    main()
