import os
import json
from moviepy.editor import VideoFileClip

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

STATE_PATH = os.path.join(PROJECT_ROOT, "nlp_command_parser", "editor_state.json")
DECISIONS_PATH = os.path.join(
    PROJECT_ROOT,
    "visual_decision_engine",
    "visual_decisions.json"
)

BASE_VIDEO = os.path.join(PROJECT_ROOT, "renderer", "base.mp4")
CAPTIONED_VIDEO = os.path.join(PROJECT_ROOT, "renderer", "output.mp4")

OUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUT_DIR, exist_ok=True)

# -------------------------
# Utilities
# -------------------------
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def rank_segments(decisions, k=3):
    scored = []
    for d in decisions:
        score = 0
        score += 2 if d.get("emphasis") else 0
        score += 1 if d.get("overlay") else 0
        scored.append((score, d))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [d for _, d in scored[:k]]

# -------------------------
# Export helpers
# -------------------------
def export_16x9(video, start, end, out_path):
    clip = video.subclip(start, end)
    clip.write_videofile(
        out_path,
        codec="libx264",
        audio_codec="aac",
        verbose=False,
        logger=None
    )

def export_9x16(video, start, end, out_path):
    clip = video.subclip(start, end)
    w, h = clip.w, clip.h

    target_w = int(h * 9 / 16)
    x_center = w // 2
    x1 = max(0, x_center - target_w // 2)
    x2 = min(w, x_center + target_w // 2)

    vertical = clip.crop(x1=x1, x2=x2)
    vertical.write_videofile(
        out_path,
        codec="libx264",
        audio_codec="aac",
        verbose=False,
        logger=None
    )

# -------------------------
# Main
# -------------------------
def main():
    state = load_json(STATE_PATH)
    highlights = state.get("highlights", {})

    if not highlights.get("enabled", False):
        print("ℹ️ Highlights disabled. Skipping.")
        return

    include_captions = highlights.get("include_captions", True)
    vertical_enabled = highlights.get("vertical", False)

    source_video_path = CAPTIONED_VIDEO if include_captions else BASE_VIDEO

    if not os.path.exists(source_video_path):
        print("❌ Source video not found:", source_video_path)
        return

    video = VideoFileClip(source_video_path)
    decisions = load_json(DECISIONS_PATH)
    picks = rank_segments(decisions)

    for i, seg in enumerate(picks, 1):
        out_16x9 = os.path.join(OUT_DIR, f"highlight_{i}_16x9.mp4")
        export_16x9(video, seg["start"], seg["end"], out_16x9)
        print(f"✅ Exported {out_16x9}")

        if vertical_enabled:
            out_9x16 = os.path.join(OUT_DIR, f"highlight_{i}_9x16.mp4")
            export_9x16(video, seg["start"], seg["end"], out_9x16)
            print(f"✅ Exported {out_9x16}")

    print("✨ Highlight generation complete")

if __name__ == "__main__":
    main()
