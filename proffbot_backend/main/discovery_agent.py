# main/discovery_prompter.py

from typing import List, Dict
import openai

GENERIC_DISCOVERY_PROMPT = """
You are an assistant helping decide whether a user's question is too vague or general.

Your job:
- Analyze the user's message and the chatbot’s current answer.
- If the user's question is specific (clear topic, intent, and well-formed), return: "SPECIFIC".
- If it's generic or broad (e.g., "Tell me about AI", "What does Adnan do?", "What are your skills?"), return:
  "GENERIC: [suggest 1–2 deeper follow-up questions to guide the user]".

User message:
{user_message}

Chatbot response:
{bot_response}
---
Verdict?
"""

def discovery_prompt_check(user_message: str, bot_response: str) -> str:
    prompt = GENERIC_DISCOVERY_PROMPT.format(
        user_message=user_message.strip(),
        bot_response=bot_response.strip()
    )

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()
