import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

VIDEO_PATH = os.path.join(BASE_DIR, "../input_video/raw.mp4")
CAPTIONS_PATH = os.path.join(BASE_DIR, "../caption_engine/captions.json")
STATE_PATH = os.path.join(BASE_DIR, "../nlp_command_parser/editor_state.json")
OUTPUT_PATH = os.path.join(BASE_DIR, "output.mp4")

FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

CONTEXT_COLORS = {
    "intro": (255, 215, 0),        # warm yellow
    "body": (255, 255, 255),       # white
    "conclusion": (0, 255, 255)    # cyan
}

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def render_caption_image(words, width, height):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    x_cursor = width // 2
    y = height - 120

    # measure total width first
    temp_font = ImageFont.truetype(FONT_REGULAR, 40)
    total_width = sum(draw.textlength(w["text"] + " ", font=temp_font) for w in words)
    x_cursor -= int(total_width // 2)

    for w in words:
        emphasized = w["emphasis"]
        font = ImageFont.truetype(FONT_BOLD if emphasized else FONT_REGULAR, 40)
        color = CONTEXT_COLORS.get(w["context"], (255, 255, 255))

        draw.text((x_cursor, y), w["text"] + " ", font=font, fill=color)
        x_cursor += draw.textlength(w["text"] + " ", font=font)

    return np.array(img)

def create_caption_clip(caption, state, video_w, video_h):
    img = render_caption_image(caption["words"], video_w, video_h)
    clip = ImageClip(img, transparent=True)
    clip = clip.set_start(caption["start"]).set_end(caption["end"])

    if state["animations"]["enabled"]:
        if any(w["emphasis"] for w in caption["words"]):
            clip = clip.resize(lambda t: 1 + 0.04 * min(t, 0.15))

    return clip

def main():
    video = VideoFileClip(VIDEO_PATH)
    captions = load_json(CAPTIONS_PATH)
    state = load_json(STATE_PATH)

    overlays = [
        create_caption_clip(c, state, video.w, video.h)
        for c in captions
    ]

    final = CompositeVideoClip([video] + overlays)
    final.write_videofile(
        OUTPUT_PATH,
        codec="libx264",
        audio_codec="aac"
    )

    print("✅ Final video rendered with kinetic typography:", OUTPUT_PATH)

if __name__ == "__main__":
    main()
