# ✅ 1. Imports and .env loading
from collections import defaultdict
from typing import  Optional, List, Dict
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from utils.preproccsing import run_preprocessing
from main.prompt_builder import system_prompt
from main.load_data import profile_data, summary
from main.discovery_agent import discovery_prompt_check
from main.critique_agent import evaluate_and_fix_response
from main.intent_agent import maybe_add_lead_followup
from tools.record import tools
from main.chat_runner import run_chat_completion
from tools.record import tools,tool_dispatch
import json




session_lead_counter = defaultdict(int)
user_turn_tracker = {}

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://AdnanLatif-proffbot-adnan.hf.space"],  # 🔒 Orestrict this to just HF frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], )

run_preprocessing() 
_cached_prompt = system_prompt(summary, profile_data)

class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]]
    session_id: Optional[str] = None
    clear: Optional[bool] = False  # ✅ Add this if not already present
    class Config:
        extra = "allow"



@app.post("/chat")
def chat_handler(req: ChatRequest):
    if not req.message or not isinstance(req.message, str):
        raise HTTPException(status_code=400, detail="Invalid or missing user message.")
    
    if not isinstance(req.history, list):
        raise HTTPException(status_code=400, detail="Invalid history format.")

    if getattr(req, "clear", False):
        session_id = req.session_id or str(id(req))
        user_turn_tracker.pop(session_id, None)
        session_lead_counter.pop(session_id, None)
        print("🧹 Session cleared from trackers.")

    session_id = req.session_id or "default"
    print(f"📡 Session ID: {session_id}")

    messages = [{"role": "system", "content": _cached_prompt}] + req.history + [{"role": "user", "content": req.message}]

    # Run the core chat
    response_obj = run_chat_completion(messages)
    response_text = response_obj["content"]
    tool_calls = response_obj.get("tool_calls", [])

    # Optional logging of tool calls
    if tool_calls:
        print(f"🔧 Tool calls triggered ({len(tool_calls)}):")
        for call in tool_calls:
            print(f"[TOOL CALL] ID={call.id}, name={call.function.name}, args={call.function.arguments}")
    
    # Self-critique and retry loop
    response_text = evaluate_and_fix_response(
        user_message=req.message,
        user_history=req.history,
        raw_response=response_text,
        tools=tools
    )

    # Discovery suggestions
    discovery_result = discovery_prompt_check(req.message, response_text or "")
    print(f"🔍 Discovery check: {discovery_result}")

    if discovery_result.startswith("GENERIC:"):
        followups = discovery_result.replace("GENERIC:", "").strip()
        response_text = (response_text or "") + f"\n\n💡 You might also want to explore:\n{followups}"

    # Lead intent logic with followup trigger
    response_text = maybe_add_lead_followup(
        session_id=session_id,
        req_history=req.history,
        req_message=req.message,
        response_text=response_text,
        session_tracker=session_lead_counter
    )

    print("📝 Final response payload:", [response_text])
    return {"response": [response_text]}




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



