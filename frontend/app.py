import streamlit as st
import subprocess
import json
import os
import sys
from pathlib import Path

# -----------------------------
# PROJECT PATHS
# -----------------------------

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

INPUT_VIDEO_PATH = os.path.join(
    PROJECT_ROOT, "input_video", "raw.mp4"
)

EDITOR_STATE_PATH = os.path.join(
    PROJECT_ROOT, "nlp_command_parser", "editor_state.json"
)

LAST_INTENT_PATH = os.path.join(
    PROJECT_ROOT, "nlp_command_parser", "last_intent.json"
)

OUTPUT_VIDEO_PATH = os.path.join(
    PROJECT_ROOT, "renderer", "output.mp4"
)

# -----------------------------
# HELPERS
# -----------------------------

def load_editor_state():
    if os.path.exists(EDITOR_STATE_PATH):
        with open(EDITOR_STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def load_last_intent():
    if os.path.exists(LAST_INTENT_PATH):
        with open(LAST_INTENT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def run_command_parser(command: str):
    result = subprocess.run(
        [sys.executable, "nlp_command_parser/command_parser.py"],
        input=command + "\n",
        text=True,
        capture_output=True,
        cwd=PROJECT_ROOT
    )

    try:
        parsed = json.loads(result.stdout)
        intent_payload = parsed.get("intent_payload", {})
        with open(LAST_INTENT_PATH, "w", encoding="utf-8") as f:
            json.dump(intent_payload, f, indent=2)
    except Exception:
        pass

def run_pipeline():
    subprocess.run(
        [sys.executable, "run_pipeline.py"],
        cwd=PROJECT_ROOT
    )

def save_uploaded_video(uploaded_file):
    os.makedirs(os.path.dirname(INPUT_VIDEO_PATH), exist_ok=True)
    with open(INPUT_VIDEO_PATH, "wb") as f:
        f.write(uploaded_file.read())

# -----------------------------
# STREAMLIT CONFIG
# -----------------------------

st.set_page_config(
    page_title="AI Automated Video Editor",
    layout="wide"
)

# -----------------------------
# CUSTOM CSS (SAFE, INLINE)
# -----------------------------

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
    }
    .section-card {
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1.2rem;
        border: 1px solid rgba(255,255,255,0.08);
    }
    .hint {
        color: #9ca3af;
        font-size: 0.85rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# HEADER
# -----------------------------

st.title("🎬 AI Automated Video Editor")
st.caption("Edit talking-head videos using natural language. No timelines. No keyframes.")

# -----------------------------
# VIDEO INPUT
# -----------------------------

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("📤 Upload Video")

uploaded_video = st.file_uploader(
    "Upload a talking-head video (≤ 5 minutes)",
    type=["mp4", "mov"]
)

if uploaded_video:
    save_uploaded_video(uploaded_video)
    st.success("Video uploaded successfully. You can now run commands and render.")

st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# COMMAND INPUT
# -----------------------------

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("💬 Edit with Natural Language")

command = st.text_input(
    "Type a command",
    placeholder="e.g. Make captions bigger and move visuals to the left"
)

col1, col2 = st.columns(2)

with col1:
    if st.button("Apply Command", use_container_width=True):
        if command.strip():
            run_command_parser(command)
            st.success("Command understood and applied.")

with col2:
    if st.button("Render Video", use_container_width=True):
        run_pipeline()
        st.success("Video rendered successfully.")

st.markdown('<div class="hint">Try commands like: “remove background boxes”, “use slide animations”, “disable b-roll”.</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# STATE + AI INTERPRETATION
# -----------------------------

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("🧠 AI Understanding")

with st.expander("AI Interpretation (for transparency)"):
    intent_data = load_last_intent()
    if intent_data:
        intents = intent_data.get("intents", [])
        confidence = intent_data.get("confidence", 0)

        if intents:
            for intent in intents:
                st.write(f"• **{intent['intent']}** → {intent.get('slots', {})}")
        else:
            st.write("No clear intent detected.")

        st.markdown(f"**Confidence:** `{confidence:.2f}`")
    else:
        st.write("No command processed yet.")

with st.expander("Current Editor State"):
    st.json(load_editor_state())

st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# OUTPUT PREVIEW
# -----------------------------

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("🎞️ Output Preview")

if os.path.exists(OUTPUT_VIDEO_PATH):
    st.video(OUTPUT_VIDEO_PATH)
else:
    st.info("Render the video to preview output here.")

st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# FOOTER
# -----------------------------

st.caption("⚙️ Automation-first • JSON-driven • Explainable AI")
