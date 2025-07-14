import os
import json
import re

# Example: path to data/Profile_Adnan_Latif.txt
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "data"))
INPUT_PATH = os.path.join(DATA_DIR, "Profile_Adnan_Latif.txt")
OUTPUT_PATH = os.path.join(DATA_DIR, "structured_profile.json")

# Read full file content
with open(INPUT_PATH, "r", encoding="utf-8") as f:
    text = f.read()

# Split by the delimiter line
raw_sections = [s.strip() for s in text.split("#" ) if s.strip()]

# Known section headers to match against
expected_sections = [
    "Summary",
    "Core competencies",
    "Business impact",
    "Experience",
    "Education",
    "Skills",
    "Licenses & certifications",
    "Languages",
    "Publications",
    "Recommendations",
    "Key Areas Led by Adnan at Bluware",
    "Key Projects Delivered by Adnan's Team at Bluware",
    "Key Areas and Projects Delivered by the Team Led by Adnan at SIRIUS",
]

# Normalize and map section titles to standard keys
def to_snake_case(text):
    return re.sub(r"[^a-z0-9]+", "_", text.strip().lower()).strip("_")

structured = {}
for section in raw_sections:
    lines = section.splitlines()
    if not lines:
        continue
    title = lines[0].strip()
    body = "\n".join(lines[1:]).strip()
    key = to_snake_case(title)
    structured[key] = body

# Save as JSON
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(structured, f, indent=2)

print(f"✅ Structured profile saved to {OUTPUT_PATH}")
