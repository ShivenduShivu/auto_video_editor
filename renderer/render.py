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


FONT_PATH_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_PATH_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def create_text_image(text, bold, width, height):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    font_path = FONT_PATH_BOLD if bold else FONT_PATH_REGULAR
    font = ImageFont.truetype(font_path, 40)

    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_w = text_bbox[2] - text_bbox[0]
    text_h = text_bbox[3] - text_bbox[1]

    x = (width - text_w) // 2
    y = height - 120

    draw.text((x, y), text, font=font, fill="white")
    return np.array(img)

def create_caption_clip(caption, state, video_w, video_h):
    img_array = create_text_image(
        caption["text"],
        state["caption_style"]["bold"],
        video_w,
        video_h
    )

    clip = ImageClip(img_array, transparent=True)
    clip = clip.set_start(caption["start"]).set_end(caption["end"])

    if state["animations"]["enabled"]:
        if caption["animation"] == "fade_in":
            clip = clip.fadein(0.3)
        elif caption["animation"] == "pop":
            clip = clip.resize(lambda t: 1 + 0.05 * min(t, 0.2))

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

    print("✅ Final video rendered:", OUTPUT_PATH)

if __name__ == "__main__":
    main()
