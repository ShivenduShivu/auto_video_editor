import os
import json
import subprocess
import sys
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
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

# -------------------- B-ROLL (TEXT ONLY) --------------------

BROLL_TEXT_KEYWORDS = {
    "ai": "AI-Driven Editing",
    "pipeline": "Automated Pipeline",
    "automation": "Fully Automated",
    "caption": "Smart Captions",
    "subtitles": "Smart Subtitles",
    "editor": "AI Video Editor"
}

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
    draw.rounded_rectangle(box, radius=radius, fill=fill)

def render_caption_block(words, width, style):
    font_size = FONT_SIZES["title"] if style == "title" else FONT_SIZES["normal"]
    font_path = FONT_BOLD if style in ["title", "emphasis"] else FONT_REGULAR
    font = ImageFont.truetype(font_path, font_size)

    max_text_width = width - 160

    lines = []
    current_line = []
    dummy = Image.new("RGBA", (10, 10))
    d = ImageDraw.Draw(dummy)

    for w in words:
        text = w.get("text") or w.get("word")
        if not text:
            continue

        test = " ".join(current_line + [text])
        if d.textlength(test, font=font) <= max_text_width:
            current_line.append(text)
        else:
            lines.append(current_line)
            current_line = [text]

        if len(lines) == 2:
            break

    if current_line and len(lines) < 2:
        lines.append(current_line)

    line_height = font_size + 8
    img_w = max(int(d.textlength(" ".join(l), font=font)) for l in lines) + PADDING * 2
    img_h = len(lines) * line_height + PADDING * 2

    img = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if style in ["title", "overlay"]:
        draw_rounded_rect(draw, (0, 0, img_w, img_h), RADIUS, COLORS["bg"])

    y = PADDING
    for line in lines:
        line_text = " ".join(line)
        line_width = int(d.textlength(line_text, font=font))
        x = (img_w - line_width) // 2

        for word in line:
            color = COLORS["accent"] if any(
                w.get("word") == word and w.get("emphasized") for w in words
            ) else COLORS["text"]
            draw.text((x, y), word + " ", font=font, fill=color)
            x += int(font.getlength(word + " "))

        y += line_height

    return img

def render_text_broll(label):
    font = ImageFont.truetype(FONT_BOLD, 30)

    dummy = Image.new("RGBA", (10, 10))
    d = ImageDraw.Draw(dummy)

    text_w = int(d.textlength(label, font=font))
    img_w = text_w + PADDING * 2
    img_h = 56

    img = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw_rounded_rect(draw, (0, 0, img_w, img_h), RADIUS, COLORS["bg"])
    draw.text((PADDING, 12), label, font=font, fill=COLORS["text"])

    return img

# -------------------- MAIN --------------------

def main():
    state = load_json(STATE_PATH)
    broll_enabled = state.get("broll", {}).get("enabled", False)

    captions = load_json(ensure_translated_captions())
    decisions = load_json(DECISIONS_PATH)
    decision_map = {d["segment_index"]: d for d in decisions}

    video = VideoFileClip(VIDEO_PATH)
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

        caption_img = render_caption_block(seg["words"], video.w, style)

        pos_y = (
            video.h * 0.25 if style == "title"
            else video.h * 0.78 if style == "overlay"
            else video.h * 0.82
        )

        overlays.append(
            ImageClip(np.array(caption_img))
            .set_start(seg["start"])
            .set_end(seg["end"])
            .set_position(("center", pos_y))
            .fadein(0.2)
            .fadeout(0.2)
        )

        # -------- TEXTUAL B-ROLL (SAFE) --------
        if broll_enabled:
            label = None
            for w in seg["words"]:
                text = (w.get("word") or w.get("text") or "").lower()
                for key, val in BROLL_TEXT_KEYWORDS.items():
                    if key in text:
                        label = val
                        break
                if label:
                    break

            if label:
                broll_img = render_text_broll(label)
                overlays.append(
                    ImageClip(np.array(broll_img))
                    .set_start(seg["start"])
                    .set_end(min(seg["start"] + 2, seg["end"]))
                    .set_position((video.w - broll_img.width - 40, 40))
                    .fadein(0.3)
                    .fadeout(0.3)
                )

    final = CompositeVideoClip([video] + overlays)
    final.write_videofile(OUTPUT_PATH, codec="libx264", audio_codec="aac")
    print("✅ Final video rendered with captions + TEXTUAL B-roll")

if __name__ == "__main__":
    main()
