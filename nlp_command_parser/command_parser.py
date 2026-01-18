import json
import os
import sys

from intent_engine import extract_intent

STATE_PATH = os.path.join(os.path.dirname(__file__), "editor_state.json")

def load_state():
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(state):
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

# -----------------------------
# STATE NORMALIZATION (SAFETY)
# -----------------------------

def normalize_state(state):
    state.setdefault("caption_style", {})
    state["caption_style"].setdefault("bold", True)
    state["caption_style"].setdefault("size", "medium")
    state["caption_style"].setdefault("background", "auto")
    state["caption_style"].setdefault("animation", "subtle")

    state.setdefault("broll", {})
    state["broll"].setdefault("enabled", True)
    state["broll"].setdefault("visibility", "auto")
    state["broll"].setdefault("positioning", "right")

    state.setdefault("animations", {})
    state["animations"].setdefault("enabled", False)
    state["animations"].setdefault("default", "fade")

    state.setdefault("overlays", {})
    state["overlays"].setdefault("enabled", True)
    state["overlays"].setdefault("mode", "auto")

    state.setdefault("emphasis", {})
    state["emphasis"].setdefault("min_emphasized_words", 2)

    state.setdefault("captions", {})
    state["captions"].setdefault("language", "original")

    return state

# -----------------------------
# APPLY INTENTS (UNCHANGED)
# -----------------------------

def apply_intents(state, payload):
    intents = payload.get("intents", [])
    confidence = payload.get("confidence", 0)

    if confidence < 0.6:
        return state

    for item in intents:
        intent = item.get("intent")
        slots = item.get("slots", {})

        # ----- CAPTIONS -----
        if intent == "CAPTION_SIZE_CHANGE":
            state["caption_style"]["size"] = slots.get(
                "size", state["caption_style"]["size"]
            )

        elif intent == "CAPTION_BACKGROUND_CHANGE":
            state["caption_style"]["background"] = slots.get(
                "background", state["caption_style"]["background"]
            )

        elif intent == "CAPTION_ANIMATION_CHANGE":
            state["caption_style"]["animation"] = slots.get(
                "animation", state["caption_style"]["animation"]
            )

        # ----- B-ROLL -----
        elif intent == "BROLL_VISIBILITY_CHANGE":
            state["broll"]["visibility"] = slots.get(
                "visibility", state["broll"]["visibility"]
            )

        elif intent == "BROLL_POSITION_CHANGE":
            state["broll"]["positioning"] = slots.get(
                "position", state["broll"]["positioning"]
            )

        elif intent == "BROLL_ENABLE_DISABLE":
            state["broll"]["enabled"] = slots.get(
                "enabled", state["broll"]["enabled"]
            )

        # ----- ANIMATIONS -----
        elif intent == "ANIMATION_ENABLE_DISABLE":
            state["animations"]["enabled"] = slots.get(
                "enabled", state["animations"]["enabled"]
            )

        elif intent == "ANIMATION_STYLE_CHANGE":
            state["animations"]["default"] = slots.get(
                "style", state["animations"]["default"]
            )

        # ----- OVERLAYS -----
        elif intent == "OVERLAY_ENABLE_DISABLE":
            state["overlays"]["enabled"] = slots.get(
                "enabled", state["overlays"]["enabled"]
            )

        elif intent == "OVERLAY_MODE_CHANGE":
            state["overlays"]["mode"] = slots.get(
                "mode", state["overlays"].get("mode", "auto")
            )

    return state

# -----------------------------
# ENTRY POINT
# -----------------------------

def parse_command(command: str):
    state = normalize_state(load_state())
    payload = extract_intent(command)
    state = apply_intents(state, payload)
    save_state(state)
    return state, payload

if __name__ == "__main__":
    cmd = sys.stdin.read().strip()
    if not cmd:
        sys.exit(1)

    updated_state, payload = parse_command(cmd)

    print(json.dumps({
        "intent_payload": payload,
        "updated_state": updated_state
    }, indent=2))
