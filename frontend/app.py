import streamlit as st
import shutil
import subprocess
import os
import time
import json

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INPUT_VIDEO_PATH = os.path.join(PROJECT_ROOT, "input_video", "raw.mp4")
OUTPUT_VIDEO_PATH = os.path.join(PROJECT_ROOT, "renderer", "output.mp4")
STATE_PATH = os.path.join(PROJECT_ROOT, "nlp_command_parser", "editor_state.json")
HIGHLIGHTS_SCRIPT = os.path.join(PROJECT_ROOT, "highlights", "generate_highlights.py")
HIGHLIGHTS_DIR = os.path.join(PROJECT_ROOT, "highlights", "outputs")

st.set_page_config(page_title="Automated Video Editor", layout="centered")

# -------------------------------
# Helpers
# -------------------------------
def load_editor_state():
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_editor_state(state):
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

# -------------------------------
# Header
# -------------------------------
st.title("🎬 Automated Talking-Head Video Editor")
st.write(
    "Edit videos using **natural language**. "
    "No timeline. No keyframes. Just intelligent automation."
)

st.markdown("---")

# -------------------------------
# Session State
# -------------------------------
if "has_rendered" not in st.session_state:
    st.session_state.has_rendered = False

if "editor_state" not in st.session_state:
    st.session_state.editor_state = load_editor_state()

# -------------------------------
# Upload Section
# -------------------------------
st.subheader("📤 Upload Video")

uploaded_file = st.file_uploader(
    "Talking-head video (≤ 5 minutes)",
    type=["mp4", "mov"]
)

if uploaded_file:
    with open(INPUT_VIDEO_PATH, "wb") as f:
        shutil.copyfileobj(uploaded_file, f)

    st.success("✅ Video uploaded")

    if st.button("🚀 Run Automated Edit (Initial Render)"):
        st.info("⏳ Running full pipeline (original language captions)")

        # 🔑 CRITICAL FIX:
        # Always reset language to ORIGINAL on initial render
        state = load_editor_state()
        state.setdefault("captions", {})
        state["captions"]["language"] = "original"
        save_editor_state(state)
        st.session_state.editor_state = state

        progress = st.progress(0)
        status = st.empty()

        steps = [
            ("Extracting audio", ["python", "audio_processing/extract_audio.py"]),
            ("Transcribing speech", ["python", "transcription/transcribe.py"]),
            ("Segmenting content", ["python", "segmentation/segmenter.py"]),
            ("Generating captions", ["python", "caption_engine/captions.py"]),
            ("Making visual decisions", ["python", "visual_decision_engine/decision_engine.py"]),
            ("Rendering video", ["python", "renderer/render.py"]),
        ]

        for i, (label, command) in enumerate(steps, start=1):
            status.info(f"🔄 {label}…")
            subprocess.run(command, cwd=PROJECT_ROOT)
            progress.progress(i / len(steps))
            time.sleep(0.2)

        st.session_state.has_rendered = True
        st.session_state.editor_state = load_editor_state()
        status.success("✅ Initial render complete!")

st.markdown("---")

# -------------------------------
# Video Preview
# -------------------------------
if st.session_state.has_rendered and os.path.exists(OUTPUT_VIDEO_PATH):
    st.subheader("🎬 Current Video")
    st.video(OUTPUT_VIDEO_PATH)

    with open(OUTPUT_VIDEO_PATH, "rb") as f:
        st.download_button(
            "⬇️ Download Video",
            f,
            file_name="edited_video.mp4",
            mime="video/mp4"
        )

st.markdown("---")

# -------------------------------
# Command Section (STATE ONLY)
# -------------------------------
st.subheader("💬 Edit with Natural Language")

command = st.text_input(
    "Enter command (e.g. *give captions in hindi*, *remove animations*)"
)

if st.button("✅ Apply Command"):
    if command.strip():
        subprocess.run(
            ["python", "nlp_command_parser/command_parser.py"],
            input=command + "\n",
            text=True,
            capture_output=True,
            cwd=PROJECT_ROOT
        )

        # Reload updated state
        st.session_state.editor_state = load_editor_state()
        st.success("✅ Command applied (logic updated)")
    else:
        st.warning("⚠️ Please enter a command")

# -------------------------------
# Re-render (Explicit)
# -------------------------------
if st.button("🎬 Re-render Video"):
    with st.spinner("Re-rendering video with updated logic…"):
        subprocess.run(["python", "renderer/render.py"], cwd=PROJECT_ROOT)

    st.success("✅ Video re-rendered")
    st.video(OUTPUT_VIDEO_PATH)

st.markdown("---")

# -------------------------------
# Highlights
# -------------------------------
st.subheader("✨ Generate Highlights")

if st.button("✨ Generate Highlights"):
    with st.spinner("Extracting highlights…"):
        subprocess.run(["python", HIGHLIGHTS_SCRIPT], cwd=PROJECT_ROOT)

    st.success("✅ Highlights generated")

    if os.path.exists(HIGHLIGHTS_DIR):
        for f in sorted(os.listdir(HIGHLIGHTS_DIR)):
            if f.endswith(".mp4"):
                st.video(os.path.join(HIGHLIGHTS_DIR, f))

# -------------------------------
# Debug / Trust
# -------------------------------
with st.expander("🔎 Current Editor State"):
    st.json(st.session_state.editor_state)

st.markdown("---")
st.caption("Automation-first • Explainable • No timeline UI")
