import subprocess
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

def run_step(name, command):
    print(f"\n🚀 Running: {name}")
    result = subprocess.run(command, shell=True, cwd=PROJECT_ROOT)
    if result.returncode != 0:
        print(f"❌ Failed at step: {name}")
        sys.exit(1)
    print(f"✅ Completed: {name}")

def main():
    print("\n🎬 AUTOMATED VIDEO EDITING PIPELINE STARTED")

    run_step("Audio Extraction", "python audio_processing/extract_audio.py")
    run_step("Transcription", "python transcription/transcribe.py")
    run_step("Segmentation", "python segmentation/segmenter.py")
    run_step("Caption Engine", "python caption_engine/captions.py")

    run_step("Visual Decisions", "python visual_decision_engine/decision_engine.py")
    run_step("Rendering", "python renderer/render.py")

    print("\n🏁 Pipeline finished successfully")

if __name__ == "__main__":
    main()
