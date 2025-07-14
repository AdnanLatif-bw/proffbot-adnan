import json
import sys
import os
from tools.record import record_unknown_question, record_user_details
import unittest


UNKNOWN_FILE = "logs/unknown_questions.json"
LEADS_FILE = "logs/leads.json"

class TestRecordFunctions(unittest.TestCase):

    def setUp(self):
        # Ensure log directory exists
        os.makedirs("logs", exist_ok=True)
        # Clear logs before each test
        for path in [UNKNOWN_FILE, LEADS_FILE]:
            with open(path, "w", encoding="utf-8") as f:
                json.dump([], f)

    def test_record_unknown_question(self):
        entry = {
            "question": "What is your favorite programming language?",
            "answer": "I'm sorry, I don't have that information."
        }

        record_unknown_question(entry)

        with open(UNKNOWN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0], entry)


    def test_record_user_details(self):
        entry = {
            "name": "Alice",
            "email": "alice@example.com",
            "message": "I'm interested in your services."
        }

        record_user_details(entry)

        with open(LEADS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0], entry)


    def tearDown(self):
        # Clean up test files
        for path in [UNKNOWN_FILE, LEADS_FILE]:
            if os.path.exists(path):
                os.remove(path)

if __name__ == "__main__":
    unittest.main()
