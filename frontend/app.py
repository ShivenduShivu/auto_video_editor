import streamlit as st
import shutil
import subprocess
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INPUT_VIDEO_PATH = os.path.join(PROJECT_ROOT, "input_video", "raw.mp4")
OUTPUT_VIDEO_PATH = os.path.join(PROJECT_ROOT, "renderer", "output.mp4")

st.set_page_config(page_title="Automated Video Editor", layout="centered")

st.title("🎬 Automated Talking-Head Video Editor")
st.write("Upload a raw talking-head video. The system edits it automatically.")

# -------------------------------
# Session State
# -------------------------------
if "has_rendered" not in st.session_state:
    st.session_state.has_rendered = False

# -------------------------------
# Upload Section
# -------------------------------
uploaded_file = st.file_uploader(
    "Upload a talking-head video (≤ 5 minutes)",
    type=["mp4", "mov"]
)

if uploaded_file:
    with open(INPUT_VIDEO_PATH, "wb") as f:
        shutil.copyfileobj(uploaded_file, f)

    st.success("Video uploaded successfully.")

    if st.button("🚀 Run Automated Edit"):
        with st.spinner("Running full automation pipeline..."):
            subprocess.run(["python", "audio_processing/extract_audio.py"], cwd=PROJECT_ROOT)
            subprocess.run(["python", "transcription/transcribe.py"], cwd=PROJECT_ROOT)
            subprocess.run(["python", "segmentation/segmenter.py"], cwd=PROJECT_ROOT)
            subprocess.run(["python", "caption_engine/captions.py"], cwd=PROJECT_ROOT)
            subprocess.run(["python", "visual_decision_engine/decision_engine.py"], cwd=PROJECT_ROOT)
            subprocess.run(["python", "renderer/render.py"], cwd=PROJECT_ROOT)

        st.session_state.has_rendered = True
        st.success("Initial edit complete.")

# -------------------------------
# Show Output + Edit Section
# -------------------------------
if st.session_state.has_rendered and os.path.exists(OUTPUT_VIDEO_PATH):
    st.subheader("🎬 Edited Video")
    st.video(OUTPUT_VIDEO_PATH)

    st.subheader("💬 Edit Using Natural Language")
    command = st.text_input("Try: 'remove animation' or 'make captions bolder'")

    if st.button("Apply Edit") and command.strip():
        with st.spinner("Applying edit and re-rendering..."):
            subprocess.run(
                ["python", "nlp_command_parser/command_parser.py"],
                input=command,
                text=True,
                cwd=PROJECT_ROOT
            )
            subprocess.run(["python", "renderer/render.py"], cwd=PROJECT_ROOT)

        st.success("Video updated.")
        st.video(OUTPUT_VIDEO_PATH)

st.markdown("---")
st.caption("No timeline. No keyframes. All edits are automatic and explainable.")
