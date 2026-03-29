from __future__ import annotations

from google import genai
from google.genai import types

from backend.llm.base import BaseLLM


class GeminiLLM(BaseLLM):
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash") -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = model

    def generate(self, prompt: str) -> str:
        response = self._client.models.generate_content(
            model=self._model,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.9),
        )
        return str(getattr(response, "text", "") or "").strip()
