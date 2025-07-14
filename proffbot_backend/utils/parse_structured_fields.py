import json
import re
import os


# Example: path to data/Profile_Adnan_Latif.txt
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "data"))
INPUT_PATH = os.path.join(DATA_DIR, "structured_profile.json")
OUTPUT_PATH = os.path.join(DATA_DIR, "profile_parsed.json")
EXPORT_PATH= os.path.join(DATA_DIR, "parsed_structured_data.json")

# Function to clean unicode escape sequences
def clean_unicode(input_text):
    return input_text.encode().decode('unicode_escape')

# Function to handle the parsing of experience data
def parse_experience(experience_data):
    parsed_experience = []
    blocks = experience_data.split("\n\n")  # Assuming each job is separated by two newlines
    for block in blocks:
        lines = block.strip().splitlines()
        if not lines:
            continue

        job = {
            "company": "Unknown",
            "title": "Unknown",
            "period": "",
            "location": "",
            "highlights": [],
            "skills": [],
            "projects": []  # Field to store the projects
        }

        # Parse job title and company name
        if len(lines) >= 2:
            job["title"] = clean_unicode(lines[0].strip())
            job["company"] = clean_unicode(lines[1].strip())

        # Parse period (e.g., Full-time)
        if len(lines) >= 3:
            job["period"] = clean_unicode(lines[2].strip())

        # Parse location and highlights
        if len(lines) >= 4:
            job["location"] = clean_unicode(lines[3].strip())
            job["highlights"] = [clean_unicode(line.strip()) for line in lines[4:]]

        # Parse projects (looking for patterns like "Project X: Description")
        projects = []
        for line in job["highlights"]:
            # Assuming projects are described with the format "Project X: Project Name"
            match = re.match(r"Project (\d+): (.+)", line)
            if match:
                project = {
                    "name": clean_unicode(match.group(2).strip()),
                    "description": clean_unicode(line.strip())
                }
                projects.append(project)

        # Add the extracted projects to the job
        job["projects"] = projects

        # Find and separate out skills section from the highlights
        new_highlights = []
        for line in job["highlights"]:
            if "skills:" in line.lower():
                skills_line = re.sub(r"(?i).*skills:\s*", "", line)
                job["skills"] = [clean_unicode(skill.strip()) for skill in re.split(r"[,\n]", skills_line) if skill.strip()]
            else:
                new_highlights.append(line)
        job["highlights"] = new_highlights



        parsed_experience.append(job)
    return parsed_experience

# Function to parse key areas and projects sections
def parse_key_areas_and_projects(raw_data):
    key_areas_bluware = []
    key_projects_bluware = []
    key_areas_sirius = []

    # Parse the sections for "key_areas_led_by_adnan_at_bluware"
    if "key_areas_led_by_adnan_at_bluware" in raw_data:
        key_areas_bluware = [clean_unicode(area.strip()) for area in raw_data["key_areas_led_by_adnan_at_bluware"].splitlines() if area.strip()]

    # Parse the sections for "key_projects_delivered_by_adnan_s_team_at_bluware"
    if "key_projects_delivered_by_adnan_s_team_at_bluware" in raw_data:
        key_projects_bluware = [clean_unicode(project.strip()) for project in raw_data["key_projects_delivered_by_adnan_s_team_at_bluware"].splitlines() if project.strip()]

    # Parse the sections for "key_areas_and_projects_delivered_by_the_team_led_by_adnan_at_sirius"
    if "key_areas_and_projects_delivered_by_the_team_led_by_adnan_at_sirius" in raw_data:
        key_areas_sirius = [clean_unicode(area.strip()) for area in raw_data["key_areas_and_projects_delivered_by_the_team_led_by_adnan_at_sirius"].splitlines() if area.strip()]

    return {
        "key_areas_led_by_adnan_at_bluware": key_areas_bluware,
        "key_projects_delivered_by_adnan_s_team_at_bluware": key_projects_bluware,
        "key_areas_and_projects_delivered_by_the_team_led_by_adnan_at_sirius": key_areas_sirius
    }

with open(INPUT_PATH, "r", encoding="utf-8") as f:
    raw = json.load(f)

parsed = {}

# Keep these sections as-is (plain text or long form)
for key in [
    "summary", "core_competencies", "business_impact", "bluware_key_projects",
    "bluware_key_areas", "sirius_key_projects", "recommendations", "publications"
]:
    if key in raw:
        parsed[key] = clean_unicode(raw[key]).strip()

# Skills → list
if "skills" in raw and isinstance(raw["skills"], str):
    skills = re.split(r"[,\n]", raw["skills"])
    parsed["skills"] = [clean_unicode(s.strip()) for s in skills if s.strip()]
    print("✅ Parsed skills:", parsed["skills"])  # ← Add this line

# Languages → list
if "languages" in raw:
    lines = raw["languages"].splitlines()
    parsed["languages"] = [clean_unicode(l.strip()) for l in lines if l.strip()]

# Certifications → list
if "licenses_certifications" in raw:
    lines = raw["licenses_certifications"].splitlines()
    parsed["certifications"] = [clean_unicode(l.strip()) for l in lines if l.strip()]

# Education → structured
if "education" in raw:
    parsed["education"] = []
    current = {}
    for line in raw["education"].splitlines():
        line = line.strip()
        if not line:
            continue
        match = re.match(r"(.+)\s*,\s*(\d{4}\s*-\s*\d{4})", line)
        if match:
            current["institution"] = clean_unicode(match.group(1).strip())
            current["dates"] = clean_unicode(match.group(2).strip())
            parsed["education"].append(current)
            current = {}
        elif "bachelor" in line.lower() or "master" in line.lower() or "phd" in line.lower():
            current["degree"] = line
        else:
            current["field"] = line

# Experience → structured
if "experience" in raw:
    parsed["experience"] = parse_experience(raw["experience"])

# Parsing key areas and projects
key_areas_and_projects = parse_key_areas_and_projects(raw)
parsed.update(key_areas_and_projects)

# Save result to structured profile file
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(parsed, f, indent=2, ensure_ascii=False)

# Export structured data for inspection
with open(EXPORT_PATH, "w", encoding="utf-8") as json_file:
    json.dump(parsed, json_file, indent=2, ensure_ascii=False)

print(f"✅ Profile parsed and saved to {OUTPUT_PATH}")
print(f"✅ Structured data exported to {EXPORT_PATH} for inspection.")
