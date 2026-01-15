import json
import os

STATE_PATH = "editor_state.json"

DEFAULT_STATE = {
    "caption_style": {
        "bold": False
    },
    "animations": {
        "enabled": True,
        "default": "fade"
    },
    "emphasis": {
        "min_emphasized_words": 2
    },
    "overlays": {
        "enabled": True
    }
}

def load_state():
    # If file does not exist or is empty, initialize it
    if not os.path.exists(STATE_PATH) or os.path.getsize(STATE_PATH) == 0:
        save_state(DEFAULT_STATE)
        return DEFAULT_STATE.copy()

    with open(STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(state):
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def apply_command(command, state):
    cmd = command.lower()

    if "make captions bolder" in cmd:
        state["caption_style"]["bold"] = True

    if "remove animation" in cmd or "disable animation" in cmd:
        state["animations"]["enabled"] = False

    if "enable animation" in cmd:
        state["animations"]["enabled"] = True

    if "remove overlay" in cmd or "disable overlay" in cmd:
        state["overlays"]["enabled"] = False

    if "increase emphasis" in cmd:
        state["emphasis"]["min_emphasized_words"] += 1

    if "decrease emphasis" in cmd:
        state["emphasis"]["min_emphasized_words"] = max(
            1, state["emphasis"]["min_emphasized_words"] - 1
        )

    return state

def main():
    print("💬 Enter edit command:")
    command = input("> ")

    state = load_state()
    updated_state = apply_command(command, state)
    save_state(updated_state)

    print("✅ Editor logic updated")
    print(json.dumps(updated_state, indent=2))

if __name__ == "__main__":
    main()
