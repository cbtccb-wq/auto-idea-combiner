from __future__ import annotations

import google.generativeai as genai

from backend.llm.base import BaseLLM


class GeminiLLM(BaseLLM):
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash") -> None:
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)

    def generate(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return str(getattr(response, "text", "") or "").strip()
