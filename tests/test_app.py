import unittest
from unittest.mock import patch

import app as web_app


class ChatRouteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client_patch = patch.object(web_app, "client", None)
        self.client_patch.start()
        self.addCleanup(self.client_patch.stop)
        self.client = web_app.app.test_client()

    def test_home_page_renders_in_knowledge_base_mode(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Knowledge base mode", response.data)

    def test_question_gets_knowledge_base_answer(self) -> None:
        response = self.client.post(
            "/api/chat",
            json={"question": "How do Python functions work?"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["source"], "knowledge_base")
        self.assertIn("function", response.json["answer"].lower())

    def test_help_returns_available_topics(self) -> None:
        response = self.client.post("/api/chat", json={"question": "help"})

        self.assertEqual(response.status_code, 200)
        self.assertIn("variables", response.json["answer"])

    def test_invalid_question_is_rejected(self) -> None:
        for question in ("", "   ", "x" * (web_app.MAX_QUESTION_LENGTH + 1)):
            with self.subTest(question_length=len(question)):
                response = self.client.post(
                    "/api/chat",
                    json={"question": question},
                )
                self.assertEqual(response.status_code, 400)

    def test_invalid_payload_and_history_are_rejected(self) -> None:
        invalid_payload = self.client.post("/api/chat", json=["not", "an", "object"])
        invalid_history = self.client.post(
            "/api/chat",
            json={"question": "Explain functions", "history": [{"role": "system"}]},
        )

        self.assertEqual(invalid_payload.status_code, 400)
        self.assertEqual(invalid_history.status_code, 400)

    def test_ai_answer_is_used_when_configured(self) -> None:
        with (
            patch.object(web_app, "client", object()),
            patch.object(web_app, "ask_openai", return_value="AI response"),
        ):
            response = self.client.post(
                "/api/chat",
                json={"question": "Explain decorators"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"answer": "AI response", "source": "ai"})


if __name__ == "__main__":
    unittest.main()
