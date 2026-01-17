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

def normalize(text):
    return text.lower().strip()

def parse_command(command, state):
    # Normalize aggressively
    text = " ".join(command.lower().split())

    # -------------------------
    # Highlight intent
    # -------------------------
    if "highlight" in text:
        state.setdefault("highlights", {})
        state["highlights"]["enabled"] = True

        # Explicit caption intent resolution
        wants_no_captions = any(
            phrase in text
            for phrase in [
                "without captions",
                "no captions",
                "remove captions",
                "captionless"
            ]
        )

        wants_captions = any(
            phrase in text
            for phrase in [
                "with captions",
                "add captions",
                "include captions",
                "show captions"
            ]
        )

        # 🔑 Authoritative resolution
        if wants_no_captions:
            state["highlights"]["include_captions"] = False
        elif wants_captions:
            state["highlights"]["include_captions"] = True
        # else: leave as-is (user didn't specify)

    # -------------------------
    # Caption style
    # -------------------------
    if "bold" in text:
        state.setdefault("caption_style", {})
        state["caption_style"]["bold"] = True

    # -------------------------
    # Simplicity / minimal intent
    # -------------------------
    if any(word in text for word in ["simple", "minimal", "clean"]):
        state["animations"]["enabled"] = False
        state["overlays"]["enabled"] = False
        state["emphasis"]["min_emphasized_words"] = 0

    # -------------------------
    # Animation intent
    # -------------------------
    if any(word in text for word in ["remove animation", "no animation"]):
        state["animations"]["enabled"] = False

    if "enable animation" in text:
        state["animations"]["enabled"] = True

    return state


def main():
    state = load_state()

    # 🔑 Deterministic input handling
    if not sys.stdin.isatty():
        command = sys.stdin.readline().strip()
    else:
        print("💬 Enter edit command:")
        command = input("> ").strip()

    if not command:
        print("⚠️ No command received.")
        return

    updated = parse_command(command, state)
    save_state(updated)

    print("✅ Editor logic updated")
    print(json.dumps(updated, indent=2))

if __name__ == "__main__":
    main()
