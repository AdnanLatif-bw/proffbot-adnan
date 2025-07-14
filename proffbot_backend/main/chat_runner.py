from typing import List, Dict, Any, cast
import json
from config import openai, MODEL_NAME
from openai.types.chat import ChatCompletionMessageParam
from tools.record import tool_dispatch, tools


def run_chat_completion(messages: List[Dict[str, str]]) -> str:
    done = False

    while not done:
        response = openai.chat.completions.create(
            model=MODEL_NAME,
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
                    "tool_call_id": tool_call.id,
                })

            messages.append(msg)
            messages.extend(results)
        else:
            done = True
            return choice.message.content or ""
