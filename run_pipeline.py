import subprocess
import sys
import json
import os

def run_step(name, command):
    print(f"\n🚀 Running: {name}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"❌ Failed at step: {name}")
        sys.exit(1)
    print(f"✅ Completed: {name}")

def load_editor_state():
    state_path = "nlp_command_parser/editor_state.json"
    if not os.path.exists(state_path):
        return {}
    with open(state_path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    print("\n🎬 AUTOMATED VIDEO EDITING PIPELINE STARTED")

    # Core pipeline
    run_step("Audio Extraction", "python audio_processing/extract_audio.py")
    run_step("Transcription", "python transcription/transcribe.py")
    run_step("Segmentation", "python segmentation/segmenter.py")
    run_step("Caption Engine", "python caption_engine/captions.py")
    run_step("Visual Decisions", "python visual_decision_engine/decision_engine.py")
    run_step("Rendering", "python renderer/render.py")

    print("\n🎉 Main video render complete")

    # Optional highlight generation (state-driven)
    state = load_editor_state()
    highlights_cfg = state.get("highlights", {})

    if highlights_cfg.get("enabled", False):
        print("\n✨ Highlights enabled — generating highlight clips")
        run_step("Highlight Generation", "python highlights/generate_highlights.py")
        print("✨ Highlight generation complete")

    print("\n🏁 Pipeline finished successfully")

if __name__ == "__main__":
    main()
