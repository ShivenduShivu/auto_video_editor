import os
import json
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# -------------------- PATHS --------------------

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

VIDEO_PATH = os.path.join(PROJECT_ROOT, "input_video", "raw.mp4")
CAPTIONS_PATH = os.path.join(PROJECT_ROOT, "caption_engine", "captions.json")
DECISIONS_PATH = os.path.join(PROJECT_ROOT, "visual_decision_engine", "visual_decisions.json")
BROLL_ASSET_DIR = os.path.join(PROJECT_ROOT, "assets", "broll")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "renderer", "output.mp4")

FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# -------------------- CONFIG --------------------

BROLL_KEYWORDS = {
    "ai": ("ai.png", "AI-Powered Editing"),
    "pipeline": ("pipeline.png", "Automated Pipeline"),
    "automation": ("automation.png", "Fully Automated"),
    "caption": ("captions.png", "Smart Captions"),
    "editor": ("editor.png", "AI Video Editor"),
}

COLORS = {
    "text": (255, 255, 255, 255),
    "accent": (255, 200, 0, 255),
    "bg": (0, 0, 0, 170),  # translucent black (Odysser-like)
}

PADDING = 24
RADIUS = 18

# -------------------- UTILS --------------------

def load_json(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def draw_rounded(draw, w, h):
    draw.rounded_rectangle((0, 0, w, h), RADIUS, COLORS["bg"])

# -------------------- B-ROLL --------------------

def render_text_broll(text):
    font = ImageFont.truetype(FONT_BOLD, 30)
    tmp = Image.new("RGBA", (10, 10))
    d = ImageDraw.Draw(tmp)
    w = int(d.textlength(text, font))
    img = Image.new("RGBA", (w + PADDING * 2, 56), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    draw_rounded(d, img.width, img.height)
    d.text((PADDING, 12), text, font=font, fill=COLORS["text"])
    return img

# -------------------- CAPTIONS --------------------

def render_caption(words, width):
    font = ImageFont.truetype(FONT_BOLD, 40)
    tmp = Image.new("RGBA", (10, 10))
    d = ImageDraw.Draw(tmp)

    line, lines = [], []
    for w in words:
        t = w.get("word") or w.get("text")
        if not t:
            continue
        test = " ".join(line + [t])
        if d.textlength(test, font) < width - 200:
            line.append(t)
        else:
            lines.append(line)
            line = [t]
    if line:
        lines.append(line)

    line_h = 48
    text_w = max(int(d.textlength(" ".join(l), font)) for l in lines)
    img_w = text_w + PADDING * 2
    img_h = len(lines) * line_h + PADDING * 2

    img = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # 🔥 Restore Odysser-style background
    draw_rounded(d, img_w, img_h)

    y = PADDING
    for ln in lines:
        text = " ".join(ln)
        x = (img_w - int(d.textlength(text, font))) // 2
        for word in ln:
            color = COLORS["accent"] if any(
                ww.get("emphasized") and ww.get("word") == word for ww in words
            ) else COLORS["text"]
            d.text((x, y), word + " ", font=font, fill=color)
            x += int(font.getlength(word + " "))
        y += line_h

    return img

# -------------------- MAIN --------------------

def main():
    captions = load_json(CAPTIONS_PATH)
    decisions = load_json(DECISIONS_PATH)
    decision_map = {d["segment_index"]: d for d in decisions}

    video = VideoFileClip(VIDEO_PATH)
    caption_layer, broll_layer = [], []

    for i, seg in enumerate(captions):
        # -------- CAPTIONS (TOP LAYER) --------
        cap = render_caption(seg["words"], video.w)
        caption_layer.append(
            ImageClip(np.array(cap))
            .set_start(seg["start"])
            .set_end(seg["end"])
            .set_position(("center", video.h * 0.75))  # 🔥 moved UP safely
            .fadein(0.15)
            .fadeout(0.15)
        )

        # -------- B-ROLL (BELOW CAPTIONS) --------
        label, icon = None, None
        for w in seg["words"]:
            t = (w.get("word") or "").lower()
            for k, (f, txt) in BROLL_KEYWORDS.items():
                if k in t:
                    icon = os.path.join(BROLL_ASSET_DIR, f)
                    label = txt
                    break
            if label:
                break

        if not label and i == 0:
            label = "AI-Powered Video Editing"
            icon = os.path.join(BROLL_ASSET_DIR, "ai.png")

        if icon and os.path.exists(icon):
            im = Image.open(icon).convert("RGBA")
            scale = 80 / im.height
            im = im.resize((int(im.width * scale), 80), Image.Resampling.LANCZOS)
            broll_layer.append(
                ImageClip(np.array(im))
                .set_start(seg["start"])
                .set_end(seg["start"] + 2)
                .set_position((video.w - im.width - 40, 40))
                .fadein(0.2)
                .fadeout(0.2)
            )
        elif label:
            txt = render_text_broll(label)
            broll_layer.append(
                ImageClip(np.array(txt))
                .set_start(seg["start"])
                .set_end(seg["start"] + 2)
                .set_position((video.w - txt.width - 40, 40))
                .fadein(0.2)
                .fadeout(0.2)
            )

    CompositeVideoClip([video] + broll_layer + caption_layer)\
        .write_videofile(OUTPUT_PATH, codec="libx264", audio_codec="aac")

    print("✅ Final render with Odysser-style captions + B-roll")

if __name__ == "__main__":
    main()
