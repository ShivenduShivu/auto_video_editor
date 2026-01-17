import json
import os
import sys

STATE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "editor_state.json"
)

def load_state():
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(state):
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def parse_command(command, state):
    text = " ".join(command.lower().split())

    # -------- Highlights --------
    if "highlight" in text:
        state["highlights"]["enabled"] = True
        if "without captions" in text:
            state["highlights"]["include_captions"] = False
        if "with captions" in text:
            state["highlights"]["include_captions"] = True

    # -------- Caption Language --------
    if "hindi" in text:
        state["captions"]["language"] = "hi"
    elif "telugu" in text:
        state["captions"]["language"] = "te"
    elif "english" in text:
        state["captions"]["language"] = "en"
    elif "original" in text:
        state["captions"]["language"] = "original"

    return state

def main():
    state = load_state()

    command = (
        sys.stdin.readline().strip()
        if not sys.stdin.isatty()
        else input("> ").strip()
    )

    if not command:
        print("⚠️ No command received.")
        return

    save_state(parse_command(command, state))
    print("✅ Editor logic updated")

if __name__ == "__main__":
    main()
