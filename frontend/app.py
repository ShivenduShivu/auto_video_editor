import streamlit as st
import shutil
import subprocess
import os
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INPUT_VIDEO_PATH = os.path.join(PROJECT_ROOT, "input_video", "raw.mp4")
OUTPUT_VIDEO_PATH = os.path.join(PROJECT_ROOT, "renderer", "output.mp4")

st.set_page_config(
    page_title="Automated Video Editor",
    layout="centered"
)

# -------------------------------
# Header
# -------------------------------
st.title("🎬 Automated Talking-Head Video Editor")
st.write(
    "Upload a raw talking-head video. "
    "The system automatically generates captions, emphasis, and animations — "
    "**no timeline, no keyframes**."
)

st.markdown("---")

# -------------------------------
# Session State
# -------------------------------
if "has_rendered" not in st.session_state:
    st.session_state.has_rendered = False

# -------------------------------
# Upload Section
# -------------------------------
st.subheader("📤 Upload Video")

uploaded_file = st.file_uploader(
    "Talking-head video (≤ 5 minutes, single speaker)",
    type=["mp4", "mov"]
)

if uploaded_file:
    with open(INPUT_VIDEO_PATH, "wb") as f:
        shutil.copyfileobj(uploaded_file, f)

    st.success("✅ Video uploaded successfully.")

    if st.button("🚀 Run Automated Edit"):
        st.info("⏳ Estimated time: ~1–3 minutes depending on video length")

        progress = st.progress(0)
        status = st.empty()

        steps = [
            ("Extracting audio", ["python", "audio_processing/extract_audio.py"]),
            ("Transcribing speech", ["python", "transcription/transcribe.py"]),
            ("Segmenting content", ["python", "segmentation/segmenter.py"]),
            ("Generating captions", ["python", "caption_engine/captions.py"]),
            ("Making visual decisions", ["python", "visual_decision_engine/decision_engine.py"]),
            ("Rendering final video", ["python", "renderer/render.py"]),
        ]

        for i, (label, command) in enumerate(steps, start=1):
            status.info(f"🔄 {label}…")
            subprocess.run(command, cwd=PROJECT_ROOT)
            progress.progress(i / len(steps))
            time.sleep(0.2)  # smooth UI update

        st.session_state.has_rendered = True
        status.success("✅ Automated edit complete!")

st.markdown("---")

# -------------------------------
# Output + Edit Section
# -------------------------------
if st.session_state.has_rendered and os.path.exists(OUTPUT_VIDEO_PATH):
    st.subheader("🎬 Edited Video Preview")
    st.video(OUTPUT_VIDEO_PATH)

    with open(OUTPUT_VIDEO_PATH, "rb") as f:
        st.download_button(
            label="⬇️ Download Video",
            data=f,
            file_name="edited_video.mp4",
            mime="video/mp4"
        )

    st.markdown("---")

    st.subheader("💬 Edit Using Natural Language")
    st.caption(
        "Example commands: `remove animation`, `make captions bolder`, `increase emphasis`"
    )

    command = st.text_input("Enter edit command")

    if st.button("Apply Edit") and command.strip():
        with st.spinner("Applying edit and re-rendering…"):
            subprocess.run(
                ["python", "nlp_command_parser/command_parser.py"],
                input=command,
                text=True,
                cwd=PROJECT_ROOT
            )
            subprocess.run(["python", "renderer/render.py"], cwd=PROJECT_ROOT)

        st.success("✅ Video updated.")
        st.video(OUTPUT_VIDEO_PATH)

        with open(OUTPUT_VIDEO_PATH, "rb") as f:
            st.download_button(
                label="⬇️ Download Updated Video",
                data=f,
                file_name="edited_video_updated.mp4",
                mime="video/mp4"
            )

st.markdown("---")
st.caption("Automation-first editing • Explainable decisions • No timeline UI")
