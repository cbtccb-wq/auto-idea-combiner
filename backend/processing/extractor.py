from __future__ import annotations

from collections import Counter
from functools import lru_cache

from backend.processing.cleaner import clean_text


STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "from",
    "into",
    "your",
    "idea",
    "using",
    "about",
    "have",
    "will",
    "日本",
    "こと",
    "もの",
    "それ",
    "ため",
    "よう",
    "これ",
    "さん",
}


@lru_cache(maxsize=1)
def _get_tokenizer():
    from janome.tokenizer import Tokenizer

    return Tokenizer()


@lru_cache(maxsize=1)
def _get_keybert_model():
    from keybert import KeyBERT

    return KeyBERT(model="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")


def extract_nouns(text: str) -> list[str]:
    normalized = clean_text(text)
    if not normalized:
        return []

    tokenizer = _get_tokenizer()
    nouns: list[str] = []
    for token in tokenizer.tokenize(normalized):
        surface = token.surface.strip()
        if not surface or len(surface) <= 1:
            continue
        part_of_speech = token.part_of_speech.split(",")[0]
        if part_of_speech == "名詞":
            nouns.append(surface)
    return nouns


def _fallback_keywords(text: str, top_n: int) -> list[str]:
    nouns = extract_nouns(text)
    if nouns:
        counts = Counter(noun.lower() for noun in nouns if noun.lower() not in STOPWORDS)
    else:
        words = [
            word.lower()
            for word in clean_text(text).split()
            if len(word) > 2 and word.lower() not in STOPWORDS
        ]
        counts = Counter(words)
    return [keyword for keyword, _ in counts.most_common(top_n)]


def extract_keywords(text: str, top_n: int = 10) -> list[str]:
    normalized = clean_text(text)
    if not normalized:
        return []

    try:
        keybert_model = _get_keybert_model()
        keywords = keybert_model.extract_keywords(
            normalized,
            top_n=top_n,
            keyphrase_ngram_range=(1, 2),
            stop_words=None,
        )
        extracted = [keyword.strip() for keyword, _ in keywords if keyword.strip()]
        if extracted:
            return extracted[:top_n]
    except Exception:
        pass

    return _fallback_keywords(normalized, top_n=top_n)
