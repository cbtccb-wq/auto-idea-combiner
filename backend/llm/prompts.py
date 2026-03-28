from __future__ import annotations

# ---------------------------------------------------------------------------
# ライトモード: 3〜5行の短い発想カード
# ---------------------------------------------------------------------------
IDEA_GENERATION_LIGHT = """
あなたは新規アイデア発想AIです。
以下の2つの概念を組み合わせた、ひらめきのタネを1つ作ってください。

概念A: {concept_a}
概念B: {concept_b}
距離カテゴリ: {distance_category}

ルール:
- 出力はJSONのみ（前後の説明文は不要）
- すべての値は日本語
- distance_category が far のときは大胆で意外な組み合わせを優先する
- シンプルに、でも「おっ」と思わせる内容にする

出力スキーマ:
{{
  "title": "",
  "one_liner": "",
  "interesting_point": ""
}}
""".strip()

# ---------------------------------------------------------------------------
# スタンダードモード: 企画メモ程度の詳細
# ---------------------------------------------------------------------------
IDEA_GENERATION_STANDARD = """
あなたは新規事業アイデアの発想支援AIです。
次の2つの概念を組み合わせて、実装可能で面白いアイデアを1つ作ってください。

概念A: {concept_a}
概念B: {concept_b}
距離カテゴリ: {distance_category}
ユーザー文脈（参考情報）: {user_context}

要件:
- 出力はJSONのみ（前後の説明文は不要）
- すべての値は日本語の文字列
- MVPとして成立する内容にする
- distance_category が far のときは意外性・奇抜さを強める
- distance_category が near のときは実現可能性と即効性を重視する
- なぜこの2つの組み合わせが面白いのか必ず説明する

出力スキーマ:
{{
  "title": "",
  "summary": "",
  "why_interesting": "",
  "target_user": "",
  "main_tech": "",
  "mvp_outline": "",
  "differentiator": "",
  "fun_point": "",
  "risks": ""
}}
""".strip()

# ---------------------------------------------------------------------------
# ディープモード: 仕様書に近いレベルの詳細
# ---------------------------------------------------------------------------
IDEA_GENERATION_DEEP = """
あなたは新規事業アイデアの発想支援AIです。
次の2つの概念を組み合わせた、詳細な事業アイデアを1つ作ってください。

概念A: {concept_a}
概念B: {concept_b}
距離カテゴリ: {distance_category}
ユーザー文脈（参考情報）: {user_context}

要件:
- 出力はJSONのみ（前後の説明文は不要）
- すべての値は日本語の文字列
- distance_category が far のときは「これは大胆だが理論上あり得る」というレベルの意外性を持たせる
- distance_category が near のときは具体的な実装ステップと差別化に集中する
- variations には異なる方向性の3パターンを必ず含める（研究向け・実用的・ぶっ飛び系）
- expansion_ideas には派生アイデアを3件含める
- なぜこの2つの組み合わせが面白いのか必ず詳述する

出力スキーマ:
{{
  "title": "",
  "summary": "",
  "why_interesting": "",
  "target_user": "",
  "main_tech": "",
  "mvp_outline": "",
  "differentiator": "",
  "fun_point": "",
  "risks": "",
  "api_candidates": "",
  "local_standalone": "",
  "variations": {{
    "research": "",
    "practical": "",
    "wild": ""
  }},
  "expansion_ideas": ["", "", ""]
}}
""".strip()

# ---------------------------------------------------------------------------
# プロンプト選択ヘルパー
# ---------------------------------------------------------------------------
_PROMPT_MAP = {
    "light": IDEA_GENERATION_LIGHT,
    "standard": IDEA_GENERATION_STANDARD,
    "deep": IDEA_GENERATION_DEEP,
}


def build_idea_generation_prompt(
    concept_a: str,
    concept_b: str,
    distance_category: str,
    user_context: str = "",
    detail_level: str = "standard",
) -> str:
    template = _PROMPT_MAP.get(detail_level, IDEA_GENERATION_STANDARD)
    kwargs: dict[str, str] = {
        "concept_a": concept_a,
        "concept_b": concept_b,
        "distance_category": distance_category,
    }
    if "{user_context}" in template:
        kwargs["user_context"] = user_context or "（なし）"
    return template.format(**kwargs)
