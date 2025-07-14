import unittest
from unittest.mock import patch
from main.critique_agent import evaluate_and_fix_response

class TestCritiqueAgent(unittest.TestCase):

    @patch("main.critique_agent.openai.chat.completions.create")
    def test_response_approved(self, mock_openai):
        # First call: critique says APPROVED
        mock_openai.return_value.choices = [
            type("obj", (object,), {"message": type("msg", (object,), {"content": "APPROVED"})})()
        ]

        response = evaluate_and_fix_response(
            user_message="What kind of AI work have you done?",
            user_history=[],
            raw_response="Adnan has worked on seismic fault detection using AI.",
            tools=[]
        )
        self.assertIn("fault detection", response)

    @patch("main.critique_agent.openai.chat.completions.create")
    def test_response_needs_rewrite(self, mock_openai):
        # Simulate two OpenAI calls: one for critique, one for retry
        def side_effect(*args, **kwargs):
            if "You are a response validator" in kwargs["messages"][0]["content"]:
                return type("obj", (object,), {
                    "choices": [type("c", (object,), {
                        "message": type("m", (object,), {"content": "REWRITE_NEEDED: too vague"})()
                    })]
                })()
            else:
                return type("obj", (object,), {
                    "choices": [type("c", (object,), {
                        "message": type("m", (object,), {"content": "Adnan led AI efforts in real-time seismic prediction."})()
                    })]
                })()

        mock_openai.side_effect = side_effect

        response = evaluate_and_fix_response(
            user_message="What do you do?",
            user_history=[{"role": "user", "content": "What do you do?"}],
            raw_response="I work in AI.",
            tools=[]
        )
        self.assertIn("real-time seismic", response)

if __name__ == "__main__":
    unittest.main()
