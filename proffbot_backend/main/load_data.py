import os
import json
from utils.preproccsing import run_preprocessing

def load_structured_data():
    file_path = "data/parsed_structured_data.json"
    summary_path = "data/summary.txt"

    # Check and regenerate if missing
    if not os.path.exists(file_path) or not os.path.exists(summary_path):
        print("⚠️ One or more files missing. Running preprocessing...")
        run_preprocessing()

    # Check again after preprocessing
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"❌ Still missing: {file_path}")
    if not os.path.exists(summary_path):
        raise FileNotFoundError(f"❌ Still missing: {summary_path}")

    # Load structured data
    with open(file_path, "r", encoding="utf-8") as f:
        structured = json.load(f)

    # Load summary
    with open(summary_path, "r", encoding="utf-8") as f:
        summary = f.read()

    return structured, summary

# Load both
profile_data, summary = load_structured_data()
