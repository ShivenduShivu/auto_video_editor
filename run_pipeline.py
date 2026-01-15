import subprocess
import sys

def run_step(name, command):
    print(f"\n🚀 Running: {name}")
    result = subprocess.run(command, shell=True)
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

    print("\n🎉 Initial render complete")

    while True:
        choice = input("\n💬 Do you want to make edits? (yes/no): ").strip().lower()
        if choice == "no":
            print("🏁 Final output ready")
            break
        elif choice == "yes":
            run_step("Chat Edit", "python nlp_command_parser/command_parser.py")
            run_step("Re-render", "python renderer/render.py")
        else:
            print("Type yes or no")

if __name__ == "__main__":
    main()
