# 🎬 Auto Video Editor  
```
                                  ╔══════════════════════════════════════════════╗
                                  ║ 🎬 AUTO VIDEO EDITOR ║
                                  ║ Automation-first AI Video Editing ║
                                  ║ No timelines • No keyframes • AI-driven ║
                                  ╚══════════════════════════════════════════════╝
```
📌 What This Is
Auto Video Editor is an automation-first, AI-driven video editing system designed to edit talking-head videos using natural language commands — with no manual timelines, no keyframes, and fully explainable decision logic.

It seamlessly converts spoken words into visuals (captions, b-roll, animations) and enables creators to generate polished videos with simple text commands.

🚀 Key Features
✔ Transcribe speech with word-level timestamps
✔ Generate smart captions (emphasis, size, animation)
✔ Add text-based and image-based B-roll automatically
✔ Command-driven editing — no timeline UI
✔ AI confidence & state diff panel
✔ Render professional 16:9/9:16 output
✔ Deterministic & JSON-driven architecture
✔ Fully traceable edit history for judges

🧠 Architecture Overview
pgsql
Copy code
User Command
      ↓
NLP Intent Parser    
      ↓
Editor State (JSON)
      ↓
Visual Decision Engine
      ↓
visual_decisions.json
      ↓
Renderer
      ↓
Final Video Output
Every step produces structured JSON.

Renderer only consumes decisions; it never invents visuals.

All AI decisions are visible and explainable.

🧩 How It Works (Example Flow)
Upload Video

Type an editing command, e.g.:

bash
Copy code
disable b-roll and make captions small
The system:

Parses intent

Updates the editor state

Generates new decisions

Renders a new video

Watch the final video — no timelines, no keyframes.

📜 Supported Natural Language Commands
Category	Example Command
Captions	make captions smaller
Captions	remove caption background
Animation	use energetic caption animation
B-Roll	disable b-roll
B-Roll	move b-roll to left
Overlays	turn off overlays

More commands can be added via the NLP intent engine.

📁 Project Structure
bash
Copy code
auto_video_editor/
├── input_video/                # Place raw.mp4 here
├── audio_processing/           # Audio extraction scripts
├── transcription/              # Speech-to-text
├── segmentation/               # Segment detection
├── caption_engine/             # Word-level captions
├── visual_decision_engine/     # Topic inference, merge state
├── nlp_command_parser/         # Intent parsing & state
├── assets/broll/               # B-roll image assets
├── renderer/                   # Video rendering logic
├── frontend/                   # Streamlit UI
├── run_pipeline.py             # Orchestration
└── requirements.txt
🛠 Installation
Clone the repo:

bash
Copy code
git clone https://github.com/ShivenduShivu/auto_video_editor.git
cd auto_video_editor
Create and activate a virtual environment:

bash
Copy code
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
Install dependencies:

bash
Copy code
pip install -r requirements.txt
▶ Usage
Run locally with Streamlit
bash
Copy code
cd auto_video_editor
streamlit run frontend/app.py
Upload & Edit
Upload a talking-head video (≤5 min)

Type commands like:

css
Copy code
disable b-roll and use subtle caption animation
Click Render Video

Preview the output

🧪 Visual Debugging & AI Transparency
The UI shows:

✔ Last parsed intent
✔ Confidence score
✔ Editor state diff
✔ Output video preview

This ensures full explainability, ideal for demo and judges.

📦 Limitations (By Design)
Single-speaker video only

Asset-based B-roll only

English captions first (multilingual later)

Local rendering (not cloud yet)

🔭 Future Scale & Features
Short Term

Face-aware B-roll positioning

More animation presets

Multilingual support

Long Term

AI-generated B-roll

Cloud rendering & queue

Multi-speaker intelligence

Plugin ecosystem

❤️ Contributing
Found a bug or want to add features?

Fork repo

Create a branch

Submit a PR

We’ll review with ❤️

📜 License
MIT License — see LICENSE for details.

🧠 Contact
👤 Shivendu Shivu
GitHub: https://github.com/ShivenduShivu
Twitter: @shivendushivu
Email: shivendu@example.com

⭐ Thanks for checking this out!
Auto Video Editor — editing that understands language.
