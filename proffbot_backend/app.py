# ✅ 1. Imports and .env loading

from typing import cast, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI
import json, os, requests
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Extra
from typing import List, Dict
from openai.types.chat import ChatCompletionMessageParam
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import subprocess
from collections import defaultdict

if Path(".env").exists():
    load_dotenv(override=True)

assert os.getenv("OPENAI_API_KEY"), "Missing OPENAI_API_KEY"
assert os.getenv("PUSHOVER_TOKEN"), "Missing PUSHOVER_TOKEN"
assert os.getenv("PUSHOVER_USER"), "Missing PUSHOVER_USER"
openai = OpenAI()

session_lead_counter = defaultdict(int)

# In-memory session-based turn tracker
user_turn_tracker = {}


#✅ 2. FastAPI setup + CORS
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://AdnanLatif-proffbot.hf.space"],  # 🔒 Orestrict this to just HF frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#✅ 3. Pushover setup
def push(text):
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": os.getenv("PUSHOVER_TOKEN"),
            "user": os.getenv("PUSHOVER_USER"),
            "message": text,
        }
    )

def record_user_details(email=None, name="Name not provided", notes="not provided"):
    if not email:
        return {"error": "Missing required email"}
    push(f"Recording {name} with email {email} and notes {notes}")
    return {"response": ["✅ User recorded."]}

def record_unknown_question(question):
    push(f"Recording {question}")
    return {"response": ["❓ Unknown question recorded."]}

#✅ 4. Tools JSON definitions
record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": { "type": "string", "description": "The email address of this user"},
            "name": { "type": "string","description": "The user's name, if they provided it"},
            "notes": {"type": "string", "description": "Any additional information about the conversation that's worth recording to give context"}
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": { "type": "string", "description": "The question that couldn't be answered"}
        },
        "required": ["question"],
        "additionalProperties": False
    }
}

tools = [{"type": "function", "function": record_user_details_json},
         {"type": "function", "function": record_unknown_question_json}]

#✅ 5. Preprocessing utility and data loader
def run_preprocessing():
    try:
        # Correct paths to the preprocessing scripts
        subprocess.run(['python', 'utils/extract_structured_profile_from_txt.py'], check=True)
        subprocess.run(['python', 'utils/parse_structured_fields.py'], check=True)
        print("Preprocessing scripts executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running the preprocessing scripts: {e}")

run_preprocessing()  # ✅ run once at startup

#✅ 5.1. Lead intent detection
# ✅ 5.1. Lead intent detection (semantic version)
def detect_lead_intent_via_llm(history: List[Dict[str, str]]) -> bool:
    prompt = """
        You are analyzing this chat history to detect if the user may be interested in a professional connection or collaboration with Adnan Latif.

        Lead intent includes both **explicit** and **indirect** signals such as:
        - Exploring Adnan’s leadership experience or strategic thinking
        - Asking about past projects or business impact
        - Questions consistent with evaluating someone for a role
        - Showing interest in collaboration, consulting, or hiring
        - Asking how to get in touch or continue the conversation

        Examples of lead intent:
        - “Would you be open to a new opportunity?”
        - “How do you usually lead AI teams?”
        - “What kind of impact do you aim for?”
        - “Would love to connect further—what’s the best way?”

        Respond with:
        - "YES" — if there are **any signs** that the user may be evaluating Adnan for hiring, partnership, consulting, or collaboration
        - "NO" — if there is clearly no such intent

        Chat history:
        {}
        ---
        Lead intent?
""".format("\n".join([f"{m['role']}: {m['content']}" for m in history if m["role"] in ["user", "assistant"]]))

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
    )
    answer = response.choices[0].message.content.strip().upper()
    return answer == "YES"





def load_structured_data():
    file_path = "me/parsed_structured_data.json"
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Missing {file_path}")
    if not os.path.exists("me/summary.txt"):
        raise FileNotFoundError("Missing summary.txt")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

#✅ 6. Prompt construction with cached data
profile_data = load_structured_data()
with open("me/summary.txt", "r", encoding="utf-8") as f:
    summary = f.read()

name= "Adnan Latif"

def system_prompt():
        prompt = f"""
        You are acting as {name}, a seasoned leader and technical expert in AI with deep expertise in machine learning, deep learning, software engineering, physics, and geoscience.\
        You have a proven track record of delivering impactful, AI-driven solutions — especially in the oil and gas industry.

            Your role is to:
            - Respond strictly based on the structured profile data provided.
            - Never generate answers from external knowledge or assumptions.
            - Represent {name} as a highly capable, credible, and visionary AI leader.

            You must:
            - Answer only with facts available in the profile data.
            - Acknowledge when information is not present by saying so.
            - Record such unanswered questions using the `record_unknown_question` tool.
            - Collect and log user emails with the `record_user_details` tool if relevant.

            Tone:
            - Be confident, approachable, and engaging — like a friendly conversation with a sharp technical mind.
            - Make each response feel human and personable, not robotic or formal.
            - Use natural language, be soft in tone, and keep the user interested with a friendly, curious vibe.
            - Adjust your vocabulary depending on whether the user is technical or non-technical.
            - Responses should be concise (~100 tokens ideal, ~200 max), with real examples from the profile wherever useful.
            - Your tone should be friendly, engaging, and human — like a confident expert who knows their stuff but is easy to talk to. \
                Responses should feel natural, not robotic or overly formal. Use soft, conversational language to keep the user interested. \
                    Adjust your level of detail depending on whether the user seems technical or non-technical.

            Conversation Strategy:
            - Understand the user’s intent or interests.
            - If AI applications are mentioned, steer toward relevant success stories or expertise.
            - Highlight how {name}'s background fits their needs or curiosity.

            Above all, stay grounded in the provided structured data. Never invent, assume, or expand beyond it.
            """

        # High-Level Summary
        prompt += f"\n\n## High-Level Summary:\n{summary}"  # High-level summary from summary.txt file
        
        # Add detailed profile sections (focusing on leadership and strategic decision-making)
        prompt += f"\n\n## Summary:\n{profile_data['summary']}"
        prompt += f"\n\n## Core Competencies (Leadership Focus):\n{profile_data['core_competencies']}"
        prompt += f"\n\n## Business Impact (Leadership Focus):\n{profile_data['business_impact']}"
        prompt += f"\n\n## Experience (Leadership & AI Strategy):\n{profile_data['experience']}"
        prompt += f"\n\n## Education (Relevant to Leadership in AI):\n{profile_data['education']}"
        prompt += f"\n\n## Skills (AI Leadership and Strategy):\n{profile_data.get('skills', 'No skills data available')}"
        prompt += f"\n\n## Licenses & Certifications (Leadership in AI):\n{profile_data['certifications']}"
        prompt += f"\n\n## Languages (Important for Global Leadership):\n{profile_data['languages']}"
        prompt += f"\n\n## Publications (AI Leadership Contributions):\n{profile_data['publications']}"
        prompt += f"\n\n## Recommendations (Leadership Focus):\n{profile_data['recommendations']}"
        prompt += f"\n\n## Key Areas Led by Adnan at Bluware (Leadership):\n{profile_data['key_areas_led_by_adnan_at_bluware']}"
        prompt += f"\n\n## Key Projects Delivered by Adnan's Team at Bluware (Leadership & AI Strategy):\n{profile_data['key_projects_delivered_by_adnan_s_team_at_bluware']}"
        prompt += f"\n\n## Key Areas and Projects Delivered by the Team Led by Adnan at SIRIUS (Leadership & AI Innovation):\n{profile_data['key_areas_and_projects_delivered_by_the_team_led_by_adnan_at_sirius']}"

        prompt += f"With this context, please chat with the user, always staying in character as {name}."
        return prompt
_cached_prompt = system_prompt()  # ✅ cache once


#✅ 7. ChatRequest class
class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]]
    session_id: Optional[str] = None
    clear: Optional[bool] = False  # ✅ Add this if not already present
    class Config:
        extra = "allow"
#✅ 8. Chat handler

@app.post("/chat")
def chat_handler(req: ChatRequest):
    if not req.message or not isinstance(req.message, str):
        raise HTTPException(status_code=400, detail="Invalid or missing user message.")
    
    if not isinstance(req.history, list):
        raise HTTPException(status_code=400, detail="Invalid history format.")

    # Optional: clear session state
    if getattr(req, "clear", False):
        session_id = req.session_id or str(id(req))
        user_turn_tracker.pop(session_id, None)
        session_lead_counter.pop(session_id, None)
        print("🧹 Session cleared from trackers.")

    session_id = req.session_id or "default"
    print(f"📡 Session ID: {session_id}")

    tool_dispatch = {
        "record_user_details": record_user_details,
        "record_unknown_question": record_unknown_question,
    }

    messages = [{"role": "system", "content": _cached_prompt}] + req.history + [{"role": "user", "content": req.message}]
    done = False

    while not done:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=cast(List[ChatCompletionMessageParam], messages),
            tools=cast(Any, tools),
            tool_choice="auto"
        )
        choice = response.choices[0]

        if choice.finish_reason == "tool_calls":
            msg = choice.message
            tool_calls = msg.tool_calls or []

            results = []
            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                try:
                    arguments = json.loads(tool_call.function.arguments)
                    tool = tool_dispatch.get(tool_name)
                    if not tool:
                        raise Exception(f"Tool '{tool_name}' not found.")
                    result = tool(**arguments)
                except Exception as e:
                    result = {"error": f"Tool call '{tool_name}' failed: {str(e)}"}

                results.append({
                    "role": "tool",
                    "content": json.dumps(result),
                    "tool_call_id": tool_call.id
                })

            messages.append(msg)
            messages.extend(results)
        else:
            done = True

    # Self-critique
    critique_prompt = f"""
You are reviewing the chatbot's response for quality and correctness.

Checklist:
1. ✅ Grounded strictly in provided profile data?
2. ✅ Does it meaningfully answer the user's question?
3. ✅ Free from hallucination or invented facts?
4. ✅ Concise (~100 tokens)?
5. ✅ Friendly, confident, human tone?

---

User message: {req.message}

Chatbot response:
\"\"\"{choice.message.content}\"\"\"

Evaluate each point. If any fail, return "REWRITE_NEEDED: [reason]". Otherwise return "APPROVED".
"""
    critique_response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a response validator for an AI chatbot."},
            {"role": "user", "content": critique_prompt},
        ],
    )
    verdict = critique_response.choices[0].message.content.strip()
    print(f"🧠 Critique verdict: {verdict}")

    if verdict.startswith("REWRITE_NEEDED"):
        retry_response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": _cached_prompt},
                *[cast(ChatCompletionMessageParam, msg) for msg in req.history],
                {"role": "user", "content": req.message},
                {"role": "assistant", "content": choice.message.content},
                {"role": "user", "content": "Please rewrite your answer in the voice of Adnan Latif, grounded strictly in the structured profile data. Make it meaningful, factual, concise, and friendly."}
            ],
            tools=cast(Any, tools),
            tool_choice="auto"
        )
        response_text = retry_response.choices[0].message.content
    else:
        response_text = choice.message.content or ""

    # Lead intent detection
    lead_intent_detected = detect_lead_intent_via_llm(
        req.history + [{"role": "user", "content": req.message}]
    )
    print(f"🤖 Semantic lead intent: {lead_intent_detected}")
    safe_response_text = str(response_text).strip()

    if lead_intent_detected:
        print("🔍 Lead intent detected!")
        session_lead_counter[session_id] += 1
        lead_count = session_lead_counter[session_id]
        print(f"📊 Lead count for session: {lead_count}")

        first_trigger = 3
        repeat_every = 5
        # Check if it's time to re-offer
        is_initial = lead_count == first_trigger
        is_repeat = (lead_count > first_trigger) and ((lead_count - first_trigger) % repeat_every == 0)


        if is_initial or is_repeat:
            # Check if user was already offered followup in past turns (not current response)
            past_turns = [m["content"].lower() for m in req.history if m["role"] == "assistant"]
            print(f"🧾 Scanning this for offer phrases:\n{safe_response_text.lower()}")

            already_offered = any(
                any(phrase in turn for phrase in ["share your email",
                        "get in touch",
                        "contact",
                        "connect",
                        "provide your contact",
                        "feel free to share your contact",
                        "share your contact details",
                        "record your interest"])
                for turn in past_turns
            )

            print(f"📎 Already offered before? {already_offered}")


            if not already_offered:
                followup = (
                    "\n\n💬 It looks like you're interested in connecting or collaborating.\n"
                    "Would you like to share your contact info so I can pass it along to Adnan?"
                )
                safe_response_text += followup

    print("📝 Final response payload:", [safe_response_text])
    return {"response": [safe_response_text]}



@app.post("/clear")
async def clear_session(req: Request):
    data = await req.json()
    session_id = data.get("session_id")
    if session_id:
        user_turn_tracker.pop(session_id, None)
        print(f"🧹 Session {session_id} cleared.")
    return {"cleared": True}

@app.get("/")
def root():
    return {"status": "ok"}

#@app.get("/pushover-test")
#def pushover_test():
#    push("✅ Test message from Render backend.")
#    return {"status": "sent"}



