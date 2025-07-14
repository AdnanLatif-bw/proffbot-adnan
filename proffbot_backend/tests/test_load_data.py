import unittest
from main.load_data import profile_data, summary

class TestLoadData(unittest.TestCase):

    def test_debug_print_profile_data_and_summary(self):
        print("📄 DEBUG: summary =", summary)
        print("🧾 DEBUG: profile_data keys =", list(profile_data.keys()))
        print("🧠 DEBUG: profile_data['skills'] =", profile_data.get("skills"))
        print("🧠 DEBUG: type(profile_data['skills']) =", type(profile_data.get("skills")))

    def test_summary_is_string(self):
        self.assertIsInstance(summary, str)
        self.assertGreater(len(summary.strip()), 0)

    def test_profile_data_is_dict(self):
        self.assertIsInstance(profile_data, dict)

    def test_required_keys_present(self):
        required_keys = [
            "summary",
            "core_competencies",
            "business_impact",
            "experience",
            "education",
            "skills",
            "certifications",
            "languages",
            "publications",
            "recommendations",
            "key_areas_led_by_adnan_at_bluware",
            "key_projects_delivered_by_adnan_s_team_at_bluware",
            "key_areas_and_projects_delivered_by_the_team_led_by_adnan_at_sirius"
        ]
        for key in required_keys:
            self.assertIn(key, profile_data, f"Missing key: {key}")

    def test_skills_is_list_or_string(self):
        skills = profile_data.get("skills")
        self.assertIsNotNone(skills, "Skills field is missing in profile_data")
        self.assertTrue(isinstance(skills, (list, str)), "Skills should be a list or string")

if __name__ == '__main__':
    unittest.main()
