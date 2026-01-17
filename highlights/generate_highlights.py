import os
import json
from moviepy.editor import VideoFileClip

# -------------------------------------------------
# Correct, absolute path resolution
# -------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

RENDERED_VIDEO = os.path.join(PROJECT_ROOT, "renderer", "output.mp4")
DECISIONS_PATH = os.path.join(
    PROJECT_ROOT,
    "visual_decision_engine",
    "visual_decisions.json"
)
STATE_PATH = os.path.join(
    PROJECT_ROOT,
    "nlp_command_parser",
    "editor_state.json"
)
OUT_DIR = os.path.join(BASE_DIR, "outputs")

os.makedirs(OUT_DIR, exist_ok=True)

# -------------------------------------------------
# Utilities
# -------------------------------------------------

def load_json(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Required file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def rank_segments(decisions, top_k=3):
    scored = []
    for d in decisions:
        score = 0
        score += 2 if d.get("emphasis") else 0
        score += 1 if d.get("overlay") else 0
        score += min(d.get("emphasized_word_count", 0), 5)
        scored.append((score, d))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [d for _, d in scored[:top_k]]

# -------------------------------------------------
# Video Export Helpers
# -------------------------------------------------

def export_clip(video, start, end, out_path):
    clip = video.subclip(
        max(0, start - 0.5),
        min(video.duration, end + 0.5)
    )
    clip.write_videofile(
        out_path,
        codec="libx264",
        audio_codec="aac",
        verbose=False,
        logger=None
    )

def export_vertical(input_path, output_path):
    clip = VideoFileClip(input_path)
    w, h = clip.w, clip.h

    target_w = int(h * 9 / 16)
    x_center = w // 2
    x1 = max(0, x_center - target_w // 2)
    x2 = min(w, x_center + target_w // 2)

    vclip = clip.crop(x1=x1, x2=x2)
    vclip.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        verbose=False,
        logger=None
    )

# -------------------------------------------------
# Main
# -------------------------------------------------

def main():
    if not os.path.exists(RENDERED_VIDEO):
        print("❌ Rendered video not found. Run the pipeline first.")
        return

    state = load_json(STATE_PATH)
    highlights_cfg = state.get("highlights", {})

    if not highlights_cfg.get("enabled", False):
        print("ℹ️ Highlights disabled. Skipping.")
        return

    decisions = load_json(DECISIONS_PATH)
    video = VideoFileClip(RENDERED_VIDEO)

    picks = rank_segments(decisions, top_k=3)

    if not picks:
        print("⚠️ No highlight-worthy segments found.")
        return

    for i, seg in enumerate(picks, 1):
        out_169 = os.path.join(OUT_DIR, f"highlight_{i}_16x9.mp4")
        export_clip(video, seg["start"], seg["end"], out_169)
        print(f"✅ Exported {out_169}")

        if highlights_cfg.get("vertical", True):
            out_916 = os.path.join(OUT_DIR, f"highlight_{i}_9x16.mp4")
            export_vertical(out_169, out_916)
            print(f"✅ Exported {out_916}")

    print("✨ Highlight generation complete.")

if __name__ == "__main__":
    main()
