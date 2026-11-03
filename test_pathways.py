import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pathways


class PathwaysTests(unittest.TestCase):
    def make_profile(self):
        return pathways.LocalProfile(
            "Dani",
            17,
            "private note sentinel",
            "hands-on work",
            "before winter break",
        )

    def test_minors_data_boundary(self):
        profile = self.make_profile()
        captured_payloads = []

        def capture_payload(payload):
            captured_payloads.append(payload)
            return "captured"

        pathways.recommend(profile, capture_payload)

        self.assertEqual(len(captured_payloads), 1)
        payload = json.dumps(captured_payloads[0])
        self.assertNotIn(profile.name, payload)
        self.assertNotIn(str(profile.age), payload)
        self.assertNotIn(profile.advisor_note, payload)
        self.assertEqual(
            set(captured_payloads[0]),
            {"preference", "timeline", "synthetic_data"},
        )

    def test_grounding_citations(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "model-calls.log"
            with patch.object(pathways, "LOG_PATH", log_path):
                response = pathways.recommend(self.make_profile())

        self.assertIn("PRG-02", response)
        self.assertIn("Oct 20, 2026", response)
        self.assertIn("Nov 30, 2026", response)
        self.assertIn("before winter break", response)

    def test_unknowns_handling(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "model-calls.log"
            with patch.object(pathways, "LOG_PATH", log_path):
                response = pathways.recommend(self.make_profile())

        self.assertIn("cannot be confirmed", response)
        self.assertIn("ADV-01", response)

    def test_mock_call_logs_exact_payload_and_response(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "model-calls.log"
            profile = self.make_profile()
            payload = pathways.sanitize_for_llm(profile)
            with patch.object(pathways, "LOG_PATH", log_path):
                response = pathways.mock_llm(payload)

            logged_call = json.loads(log_path.read_text(encoding="utf-8").splitlines()[0])

        self.assertEqual(logged_call, {"payload": payload, "response": response})

    def test_main_does_not_prompt_for_user_input(self):
        output = StringIO()
        note = "I would like to ask about workplace visits."
        with patch("builtins.input", side_effect=AssertionError("unexpected prompt")):
            with tempfile.TemporaryDirectory() as temp_dir:
                log_path = Path(temp_dir) / "model-calls.log"
                with patch.object(pathways, "LOG_PATH", log_path):
                    with redirect_stdout(output):
                        pathways.main()
                logged_call = json.loads(log_path.read_text(encoding="utf-8").splitlines()[0])

        rendered = output.getvalue()
        self.assertLess(rendered.index("Pathways | Next-step guide"), rendered.index("Profile"))
        self.assertLess(rendered.index("Profile"), rendered.index("Recommendation"))
        self.assertIn("Name: Dani", rendered)
        self.assertIn("Age: 17", rendered)
        self.assertIn(f"Note to advisor: {note}", rendered)
        self.assertIn("Preference: hands-on work", rendered)
        self.assertIn("Timeline: before winter break", rendered)
        self.assertNotIn(note, json.dumps(logged_call["payload"]))


if __name__ == "__main__":
    unittest.main()