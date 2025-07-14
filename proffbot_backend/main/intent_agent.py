from typing import List, Dict
from config import openai, first_trigger, repeat_every, followup
from main.prompt_builder import system_prompt
from main.load_data import profile_data, summary

# Phrases we scan assistant replies for, to avoid spamming followups
already_offered_phrases = [
    "would you like me to", "interested in a", "happy to connect you", 
    "book a quick call", "i can send more details", "let me know if"
]

LEAD_INTENT_PROMPT = """
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
"""

def detect_lead_intent(conversation: List[Dict[str, str]]) -> bool:
    chat_str = "\n".join(
        f"{turn['role'].capitalize()}: {turn['content'].strip()}" for turn in conversation
    )
    prompt = LEAD_INTENT_PROMPT.format(chat_str)

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip().upper().startswith("YES")


def maybe_add_lead_followup(
    session_id: str,
    req_history: List[Dict[str, str]],
    req_message: str,
    response_text: str,
    session_tracker: Dict[str, int]
) -> str:
    if not detect_lead_intent(req_history + [{"role": "user", "content": req_message}]):
        return response_text

    print("🔍 Lead intent detected!")
    session_tracker[session_id] += 1
    lead_count = session_tracker[session_id]
    print(f"📊 Lead count for session: {lead_count}")

    is_initial = lead_count == first_trigger
    is_repeat = (lead_count > first_trigger) and ((lead_count - first_trigger) % repeat_every == 0)

    if not (is_initial or is_repeat):
        return response_text

    past_turns = [m["content"].lower() for m in req_history if m["role"] == "assistant"]
    print(f"🧾 Scanning this for offer phrases:\n{response_text.lower()}")

    already_offered = any(
        any(phrase in turn for phrase in already_offered_phrases)
        for turn in past_turns
    )
    print(f"📎 Already offered before? {already_offered}")

    if not already_offered:
        response_text += followup

    return response_text
