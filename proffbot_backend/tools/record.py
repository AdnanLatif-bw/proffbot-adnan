from tools.pushover import push

def record_user_details(email=None, name="Name not provided", notes="not provided"):
    if not email:
        return {"error": "Missing required email"}
    push(f"Recording {name} with email {email} and notes {notes}")
    return {"response": ["✅ User recorded."]}

def record_unknown_question(question):
    print(f"📊  Unknown question recorded: {question}")  # ✅ Debug print
    push(f"Recording {question}")
    return {"response": ["❓ Unknown question recorded."]}


# Tool dispatch mapping
tool_dispatch = {
    "record_user_details": record_user_details,
    "record_unknown_question": record_unknown_question,
}

# Tools metadata used in OpenAI function calling
tools = [
    {
        "type": "function",
        "function": {
            "name": "record_user_details",
            "description": "Record user info if they express interest in getting in touch.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "User's full name"},
                    "email": {"type": "string", "description": "User's email address"},
                    "reason": {"type": "string", "description": "Why they want to connect"}
                },
                "required": ["name", "email", "reason"]
            }
        },
    },
    {
        "type": "function",
        "function": {
            "name": "record_unknown_question",
            "description": "Record a question that could not be answered with current data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "The unknown or unanswerable user question"}
                },
                "required": ["question"]
            }
        },
    },
]
