import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pathways


class PathwaysTests(unittest.TestCase):
    def test_minors_data_boundary(self):
        profile = pathways.LocalProfile("Dani", 17, "private note sentinel")
        captured_prompts = []

        def capture_prompt(prompt):
            captured_prompts.append(prompt)
            return "captured"

        pathways.recommend(profile, "PRG-02", "Could you check seats?", capture_prompt)

        self.assertEqual(len(captured_prompts), 1)
        prompt = captured_prompts[0]
        self.assertNotIn(profile.name, prompt)
        self.assertNotIn(str(profile.age), prompt)
        self.assertNotIn(profile.advisor_note, prompt)
        self.assertNotIn("Could you check seats?", prompt)

    def test_grounding_citations(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "model-calls.log"
            with patch.object(pathways, "LOG_PATH", log_path):
                response = pathways.recommend(
                    pathways.LocalProfile("Dani", 17, "private note"),
                    "PRG-02",
                    "overview",
                )

        self.assertIn("PRG-02", response)
        self.assertIn("Oct 20, 2026", response)

    def test_unknowns_handling(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "model-calls.log"
            with patch.object(pathways, "LOG_PATH", log_path):
                response = pathways.recommend(
                    pathways.LocalProfile("Dani", 17, "private note"),
                    "PRG-02",
                    "Are seats available?",
                )

        self.assertIn("cannot be confirmed", response)
        self.assertIn("ADV-01", response)

    def test_unknown_start_date_and_aid_amounts_offer_advisor(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "model-calls.log"
            with patch.object(pathways, "LOG_PATH", log_path):
                profile = pathways.LocalProfile("Dani", 17, "private note")
                start_response = pathways.recommend(profile, "PRG-03", "When does it start?")
                aid_response = pathways.recommend(profile, "PRG-03", "What aid is available?")

        self.assertIn("cannot be confirmed", start_response)
        self.assertIn("ADV-01", start_response)
        self.assertIn("Exact award amounts cannot be confirmed", aid_response)
        self.assertIn("ADV-01", aid_response)

    def test_mock_call_logs_exact_prompt_and_response(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "model-calls.log"
            prompt = pathways.build_prompt("PRG-01", "overview")
            with patch.object(pathways, "LOG_PATH", log_path):
                response = pathways.mock_llm(prompt)

            logged_call = json.loads(log_path.read_text(encoding="utf-8").splitlines()[0])

        self.assertEqual(logged_call, {"prompt": prompt, "response": response})


if __name__ == "__main__":
    unittest.main()