from __future__ import annotations

from anthropic import Anthropic

from backend.llm.base import BaseLLM


class AnthropicLLM(BaseLLM):
    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-haiku-20241022",
    ) -> None:
        self.model = model
        self.client = Anthropic(api_key=api_key)

    def generate(self, prompt: str) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1200,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(
            block.text
            for block in response.content
            if getattr(block, "type", None) == "text"
        ).strip()
