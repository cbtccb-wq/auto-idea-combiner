from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Any

from backend.llm.base import BaseLLM
from backend.llm.prompts import build_idea_generation_prompt

logger = logging.getLogger(__name__)
JSON_RE = re.compile(r"\{.*\}", re.DOTALL)


class IdeaGenerator:
    def __init__(self, llm: BaseLLM) -> None:
        self._llm = llm

    async def generate(
        self,
        concept_a: str,
        concept_b: str,
        distance_category: str,
        detail_level: str = "standard",
        user_context: str = "",
    ) -> dict[str, Any]:
        prompt = build_idea_generation_prompt(
            concept_a=concept_a,
            concept_b=concept_b,
            distance_category=distance_category,
            user_context=user_context,
            detail_level=detail_level,
        )
        raw = await asyncio.to_thread(self._llm.generate, prompt)
        return self._parse(raw, concept_a, concept_b)

    async def generate_batch(
        self,
        combinations: list[tuple[str, str, str]],
        detail_level: str = "standard",
        user_context: str = "",
    ) -> list[dict[str, Any]]:
        tasks = [
            self.generate(
                concept_a=c[0],
                concept_b=c[1],
                distance_category=c[2],
                detail_level=detail_level,
                user_context=user_context,
            )
            for c in combinations
        ]
        return await asyncio.gather(*tasks, return_exceptions=False)

    @staticmethod
    def _parse(raw: str, concept_a: str, concept_b: str) -> dict[str, Any]:
        match = JSON_RE.search(raw)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                logger.warning("JSON parse failed, returning raw fallback")
        return {
            "title": f"{concept_a} × {concept_b}",
            "summary": raw[:200] if raw else "生成失敗",
            "why_interesting": "",
            "target_user": "",
            "main_tech": "",
            "mvp_outline": "",
            "differentiator": "",
            "fun_point": "",
            "risks": "",
        }
