import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are an AI video editor.

Convert a user's natural language command into
STRUCTURED EDITING INTENTS for an automated video editor.

Return STRICT JSON ONLY. No explanations. No markdown.

-----------------
EDITOR CONCEPTS
-----------------

CAPTIONS refer to:
- captions
- subtitles
- text
- words on screen

B-ROLL refers to:
- icons
- visuals
- graphics
- images
- overlays
- extra visuals
- supporting visuals

ANIMATIONS refer to:
- motion
- transitions
- effects
- movement
- fade
- slide
- pop

OVERLAYS refer to:
- background boxes
- caption background
- translucent blocks
- highlight bars
- black background behind text

-----------------
OUTPUT SCHEMA
-----------------

{
  "intents": [
    {
      "intent": "<INTENT_NAME>",
      "slots": { "<key>": "<value>" }
    }
  ],
  "confidence": <float between 0 and 1>
}

-----------------
ALLOWED INTENTS
-----------------

CAPTION_SIZE_CHANGE
  size: small | medium | large

CAPTION_BACKGROUND_CHANGE
  background: auto | always | never

CAPTION_ANIMATION_CHANGE
  animation: none | subtle | energetic

BROLL_VISIBILITY_CHANGE
  visibility: auto | prominent

BROLL_POSITION_CHANGE
  position: left | right | smart

BROLL_ENABLE_DISABLE
  enabled: true | false

ANIMATION_ENABLE_DISABLE
  enabled: true | false

ANIMATION_STYLE_CHANGE
  style: fade | slide | pop

OVERLAY_ENABLE_DISABLE
  enabled: true | false

OVERLAY_MODE_CHANGE
  mode: always | auto | minimal

-----------------
RULES
-----------------

- One command may contain MULTIPLE intents
- Use semantic meaning, not keywords
- Omit unclear intents
- confidence reflects overall understanding (0–1)
"""

def extract_intent(command: str) -> dict:
    try:
        response = client.responses.create(
            model="gpt-4o-mini",
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": command}
            ],
        )

        raw = response.output_text.strip()
        parsed = json.loads(raw)

        if not isinstance(parsed.get("intents"), list):
            raise ValueError("Invalid intent schema")

        return parsed

    except Exception:
        return {
            "intents": [],
            "confidence": 0.0
        }
