import unittest
from unittest.mock import patch
from main.discovery_prompter import discovery_prompt_check

class TestDiscoveryPrompter(unittest.TestCase):

    @patch("main.discovery_prompter.openai.chat.completions.create")
    def test_generic_question_detection(self, mock_openai):
        # Mock the OpenAI response for a generic question
        mock_openai.return_value.choices = [
            type("obj", (object,), {"message": type("msg", (object,), {"content": "GENERIC: What specific AI projects has Adnan worked on?"})})()
        ]

        user_msg = "Tell me about AI"
        bot_response = "Adnan has worked on AI systems in geoscience."
        verdict = discovery_prompt_check(user_msg, bot_response)

        self.assertTrue(verdict.startswith("GENERIC"))
        self.assertIn("What specific", verdict)

    @patch("main.discovery_prompter.openai.chat.completions.create")
    def test_specific_question_detection(self, mock_openai):
        # Mock the OpenAI response for a specific question
        mock_openai.return_value.choices = [
            type("obj", (object,), {"message": type("msg", (object,), {"content": "SPECIFIC"})})()
        ]

        user_msg = "How did Adnan apply ML in seismic interpretation?"
        bot_response = "Adnan applied machine learning to detect thin sands and reduce uncertainty in seismic workflows."

        verdict = discovery_prompt_check(user_msg, bot_response)
        self.assertEqual(verdict, "SPECIFIC")

if __name__ == "__main__":
    unittest.main()
