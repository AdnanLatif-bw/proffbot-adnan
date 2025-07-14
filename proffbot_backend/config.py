name= "Adnan Latif"
MODEL_NAME = "gpt-4o-mini"
MODEL_NAME_CRITIQUE = "gpt-4o"
MODEL_NAME_INTENT = "gpt-4o"
MODEL_NAME_RECORD = "gpt-4o"

import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# ✅ Load environment variables
if Path(".env").exists():
    load_dotenv(override=True)

# ✅ Mandatory environment checks
required_vars = ["OPENAI_API_KEY", "PUSHOVER_TOKEN", "PUSHOVER_USER"]
for var in required_vars:
    assert os.getenv(var), f"Missing {var}"

# ✅ Initialize OpenAI client
openai = OpenAI()

# Lead intent prompt control
first_trigger = 2       # Offer follow-up after 2nd lead intent
repeat_every = 3        # Then repeat every 4 turns

followup = ("\n\n💬 It looks like you're interested in connecting or collaborating.\n"
                    "Would you like to share your contact info so I can pass it along to Adnan Latif?")