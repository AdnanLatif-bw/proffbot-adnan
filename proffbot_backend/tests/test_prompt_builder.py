import unittest
from main.prompt_builder import system_prompt

class TestPromptBuilder(unittest.TestCase):

    def test_prompt_includes_summary(self):
        profile_data = {
            "summary": "Led AI initiatives at Bluware.",
            "core_competencies": "",
            "business_impact": "",
            "experience": "",
            "education": "",
            "skills": "",
            "certifications": "",
            "languages": "",
            "publications": "",
            "recommendations": "",
            "key_areas_led_by_adnan_at_bluware": "",
            "key_projects_delivered_by_adnan_s_team_at_bluware": "",
            "key_areas_and_projects_delivered_by_the_team_led_by_adnan_at_sirius": ""
        }
        summary = "Adnan is a seasoned AI leader."
        prompt = system_prompt(summary, profile_data)
        self.assertIn("Adnan is a seasoned AI leader", prompt)

    def test_empty_profile_does_not_crash(self):
        profile_data = {}
        summary = ""
        try:
            prompt = system_prompt(summary, profile_data)
            self.assertIsInstance(prompt, str)
        except Exception as e:
            self.fail(f"system_prompt crashed with empty profile: {e}")

    def test_prompt_handles_list_fields(self):
        profile_data = {
            "summary": "",
            "core_competencies": ["Leadership", "AI Strategy"],
            "business_impact": "",
            "experience": "",
            "education": "",
            "skills": ["Machine Learning", "Deep Learning", "Python"],
            "certifications": ["Certified AI Professional"],
            "languages": ["English", "Norwegian"],
            "publications": "",
            "recommendations": "",
            "key_areas_led_by_adnan_at_bluware": "",
            "key_projects_delivered_by_adnan_s_team_at_bluware": "",
            "key_areas_and_projects_delivered_by_the_team_led_by_adnan_at_sirius": ""
        }
        summary = "Global AI strategist with deep technical and leadership skills."
        prompt = system_prompt(summary, profile_data)

        # Assert key list entries are formatted correctly
        self.assertIn("- Machine Learning", prompt)
        self.assertIn("- AI Strategy", prompt)
        self.assertIn("- Certified AI Professional", prompt)
        self.assertIn("- Norwegian", prompt)

if __name__ == "__main__":
    unittest.main()
