import os
import json
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# ==================== PATHS ====================

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

VIDEO_PATH = os.path.join(PROJECT_ROOT, "input_video", "raw.mp4")
CAPTIONS_PATH = os.path.join(PROJECT_ROOT, "caption_engine", "captions.json")
DECISIONS_PATH = os.path.join(PROJECT_ROOT, "visual_decision_engine", "visual_decisions.json")
BROLL_ASSET_DIR = os.path.join(PROJECT_ROOT, "assets", "broll")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "renderer", "output.mp4")

FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# ==================== VISUAL CONSTANTS ====================

CAPTION_SLIDE_OFFSET = 12        # subtle upward motion
BROLL_SLIDE_DISTANCE = 60        # slide-in distance
CAPTION_SAFE_Y = 0.75            # vertical safe area

COLORS = {
    "text": (255, 255, 255, 255),
    "accent": (255, 200, 0, 255),
    "bg_strong": (0, 0, 0, 180),
    "bg_light": (0, 0, 0, 130),
}

PADDING = 24
RADIUS = 18

# ==================== CONFIG ====================

BROLL_KEYWORDS = {
    "ai": ("ai.png", "AI-Powered Editing"),
    "pipeline": ("pipeline.png", "Automated Pipeline"),
    "automation": ("automation.png", "Fully Automated"),
    "caption": ("captions.png", "Smart Captions"),
    "editor": ("editor.png", "AI Video Editor"),
}

# ==================== HELPERS ====================

def load_json(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def draw_bg(draw, w, h, strong=True):
    color = COLORS["bg_strong"] if strong else COLORS["bg_light"]
    draw.rounded_rectangle((0, 0, w, h), RADIUS, color)

# ==================== CAPTION RENDER ====================

def render_caption(words, width, decision):
    font = ImageFont.truetype(FONT_BOLD, 40)
    tmp = Image.new("RGBA", (10, 10))
    d = ImageDraw.Draw(tmp)

    lines, current = [], []
    for w in words:
        t = w.get("word") or w.get("text")
        if not t:
            continue
        test = " ".join(current + [t])
        if d.textlength(test, font) < width - 200:
            current.append(t)
        else:
            lines.append(current)
            current = [t]
    if current:
        lines.append(current)

    multi_line = len(lines) > 1
    use_bg = decision.get("title") or decision.get("overlay") or multi_line

    line_h = 48
    text_w = max(int(d.textlength(" ".join(l), font)) for l in lines)
    img_w = text_w + PADDING * 2
    img_h = len(lines) * line_h + PADDING * 2

    img = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    if use_bg:
        draw_bg(d, img_w, img_h, strong=decision.get("title") or decision.get("overlay"))

    y = PADDING
    for ln in lines:
        x = (img_w - int(d.textlength(" ".join(ln), font))) // 2
        for word in ln:
            color = COLORS["accent"] if any(
                ww.get("emphasized") and ww.get("word") == word for ww in words
            ) else COLORS["text"]
            d.text((x, y), word + " ", font=font, fill=color)
            x += int(font.getlength(word + " "))
        y += line_h

    return img

# ==================== B-ROLL ====================

def render_text_broll(text):
    font = ImageFont.truetype(FONT_BOLD, 30)
    tmp = Image.new("RGBA", (10, 10))
    d = ImageDraw.Draw(tmp)
    w = int(d.textlength(text, font))

    img = Image.new("RGBA", (w + PADDING * 2, 56), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    draw_bg(d, img.width, img.height, strong=False)
    d.text((PADDING, 12), text, font=font, fill=COLORS["text"])
    return img

# ==================== MAIN ====================

def main():
    captions = load_json(CAPTIONS_PATH)
    decisions = load_json(DECISIONS_PATH)
    decision_map = {d["segment_index"]: d for d in decisions}

    video = VideoFileClip(VIDEO_PATH)

    caption_layer = []
    broll_layer = []

    for i, seg in enumerate(captions):
        decision = decision_map.get(i, {})

        # -------- CAPTION --------
        cap_img = render_caption(seg["words"], video.w, decision)
        base_y = video.h * CAPTION_SAFE_Y

        caption_layer.append(
            ImageClip(np.array(cap_img))
            .set_start(seg["start"])
            .set_end(seg["end"])
            .set_position(
                lambda t, by=base_y: ("center", by + CAPTION_SLIDE_OFFSET * (1 - min(t, 0.2) / 0.2))
            )
            .fadein(0.2)
            .fadeout(0.15)
        )

        # -------- B-ROLL --------
        label, icon = None, None
        for w in seg["words"]:
            t = (w.get("word") or "").lower()
            for k, (f, txt) in BROLL_KEYWORDS.items():
                if k in t:
                    label = txt
                    icon = os.path.join(BROLL_ASSET_DIR, f)
                    break
            if label:
                break

        if not label and i == 0:
            label = "AI-Powered Video Editing"
            icon = os.path.join(BROLL_ASSET_DIR, "ai.png")

        start_x = video.w + BROLL_SLIDE_DISTANCE

        if icon and os.path.exists(icon):
            im = Image.open(icon).convert("RGBA")
            scale = 80 / im.height
            im = im.resize((int(im.width * scale), 80), Image.Resampling.LANCZOS)

            broll_layer.append(
                ImageClip(np.array(im))
                .set_start(seg["start"])
                .set_end(seg["start"] + 2)
                .set_position(lambda t: (video.w - im.width - 40 + (1 - min(t, 0.3)/0.3) * BROLL_SLIDE_DISTANCE, 40))
                .fadein(0.2)
                .fadeout(0.2)
            )
        elif label:
            txt = render_text_broll(label)
            broll_layer.append(
                ImageClip(np.array(txt))
                .set_start(seg["start"])
                .set_end(seg["start"] + 2)
                .set_position(lambda t: (video.w - txt.width - 40 + (1 - min(t, 0.3)/0.3) * BROLL_SLIDE_DISTANCE, 40))
                .fadein(0.2)
                .fadeout(0.2)
            )

    CompositeVideoClip([video] + broll_layer + caption_layer)\
        .write_videofile(OUTPUT_PATH, codec="libx264", audio_codec="aac")

    print("✅ Odysser-style captions + animated B-roll rendered")

if __name__ == "__main__":
    main()
