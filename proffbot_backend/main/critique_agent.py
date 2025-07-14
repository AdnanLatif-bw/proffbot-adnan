# main/critique_agent.py

from typing import List, Dict, Any, cast
from openai.types.chat import ChatCompletionMessageParam
from config import MODEL_NAME_CRITIQUE, openai, first_trigger, repeat_every, followup
from main.prompt_builder import system_prompt
from main.load_data import profile_data, summary

_cached_prompt = system_prompt(summary, profile_data)

critique_prompt_checklist = """ You are reviewing the chatbot's response for quality and correctness.

Checklist:
1. ✅ Grounded strictly in provided profile data?
2. ✅ Does it meaningfully answer the user's question?
3. ✅ Free from hallucination or invented facts?
4. ✅ Concise (~100 tokens)?
5. ✅ Friendly, confident, human tone?
"""

def evaluate_and_fix_response(
    user_message: str,
    user_history: List[Dict[str, str]],
    raw_response: str,
    tools: List[Dict[str, Any]]
) -> str:
    critique_prompt = f"""{critique_prompt_checklist}
User message: {user_message}
Chatbot response:
\"\"\"{raw_response}\"\"\"
Evaluate each point. If any fail, return "REWRITE_NEEDED: [reason]". Otherwise return "APPROVED".
"""
    critique_response = openai.chat.completions.create(
        model=MODEL_NAME_CRITIQUE,
        messages=[
            {"role": "system", "content": "You are a response validator for an AI chatbot."},
            {"role": "user", "content": critique_prompt},
        ],
    )
    verdict = critique_response.choices[0].message.content.strip()
    print(f"🧠 Critique verdict: {verdict}")

    if verdict.startswith("REWRITE_NEEDED"):
        retry_response = openai.chat.completions.create(
            model=MODEL_NAME_CRITIQUE,
            messages=[
                {"role": "system", "content": _cached_prompt},
                *[cast(ChatCompletionMessageParam, msg) for msg in user_history],
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": raw_response},
                {"role": "user", "content": "Please rewrite your answer in the voice of Adnan Latif, grounded strictly in the structured profile data. Make it meaningful, factual, concise, and friendly."}
            ],
            tools=cast(Any, tools),
            tool_choice="auto")
        return retry_response.choices[0].message.content or ""
    else:
        return raw_response
