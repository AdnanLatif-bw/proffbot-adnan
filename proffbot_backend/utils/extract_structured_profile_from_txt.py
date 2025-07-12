import os
import json
import re

input_path = "me/Profile_Adnan_Latif.txt"
output_path = "me/structured_profile.json"

# Create folder if not exists
os.makedirs("me", exist_ok=True)

# Read full file content
with open(input_path, "r", encoding="utf-8") as f:
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
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(structured, f, indent=2)

print(f"✅ Structured profile saved to {output_path}")
