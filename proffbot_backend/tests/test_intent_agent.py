# tests/test_intent_agent.py

import unittest
from main.intent_agent import maybe_add_lead_followup
from config import first_trigger

class TestLeadIntentAgent(unittest.TestCase):

    def setUp(self):
        self.session_id = "test-session"
        self.session_tracker = {self.session_id: first_trigger - 1}
        self.req_message = "Would you be open to collaborating?"
        self.req_history = [
            {"role": "user", "content": "Tell me about your leadership experience."},
            {"role": "assistant", "content": "I've led multiple teams across AI initiatives."}
        ]
        self.response_text = "Sure, here's a summary of my work."

    def test_no_lead_intent(self):
        # Message unrelated to lead intent
        result = maybe_add_lead_followup(
            session_id=self.session_id,
            req_history=[],
            req_message="What's your favorite programming language?",
            response_text="I enjoy using Python.",
            session_tracker={self.session_id: 0}
        )
        self.assertEqual(result, "I enjoy using Python.")

    def test_initial_lead_intent(self):
        result = maybe_add_lead_followup(
            session_id=self.session_id,
            req_history=self.req_history,
            req_message=self.req_message,
            response_text=self.response_text,
            session_tracker=self.session_tracker
        )
        self.assertIn("Would you like to share your contact info", result)
  # look for followup signal

    def test_repeated_lead_intent(self):
        # Simulate past offers and hitting repeat threshold
        self.session_tracker[self.session_id] = 4  # Assuming repeat_every = 3 and first_trigger = 1
        req_history_with_offer = [
            {"role": "assistant", "content": "I'm happy to connect you."}
        ]
        result = maybe_add_lead_followup(
            session_id=self.session_id,
            req_history=req_history_with_offer,
            req_message=self.req_message,
            response_text=self.response_text,
            session_tracker=self.session_tracker
        )
        # No new follow-up added because already offer
