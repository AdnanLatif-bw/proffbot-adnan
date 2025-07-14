import subprocess
import os

def run_preprocessing():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    extract_script = os.path.join(script_dir, "extract_structured_profile_from_txt.py")
    parse_script = os.path.join(script_dir, "parse_structured_fields.py")

    try:
        subprocess.run(['python', extract_script], check=True)
        subprocess.run(['python', parse_script], check=True)
        print("✅ Preprocessing scripts executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error while running preprocessing scripts: {e}")

if __name__ == "__main__":
    run_preprocessing()
