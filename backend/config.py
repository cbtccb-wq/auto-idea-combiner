from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(PROJECT_ROOT / ".env", BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    llm_provider: str = Field(default="anthropic", alias="LLM_PROVIDER")
    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    gemini_api_key: str | None = Field(default=None, alias="GEMINI_API_KEY")

    embedding_provider: str = Field(default="local", alias="EMBEDDING_PROVIDER")
    embedding_model: str = Field(
        default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        alias="EMBEDDING_MODEL",
    )

    backend_port: int = Field(default=8765, alias="BACKEND_PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    # str型で受けてプロパティでlist変換 (pydantic-settings v2はlist[str]をJSONパースするため)
    local_scan_dirs_raw: str = Field(default="", alias="LOCAL_SCAN_DIRS")
    clipboard_watch: bool = Field(default=True, alias="CLIPBOARD_WATCH")
    external_api_enabled: bool = Field(default=True, alias="EXTERNAL_API_ENABLED")
    chroma_persist_dir: str = Field(default="./chroma_data", alias="CHROMA_PERSIST_DIR")
    news_api_key: str | None = Field(default=None, alias="NEWS_API_KEY")
    github_token: str | None = Field(default=None, alias="GITHUB_TOKEN")

    novelty: float = Field(default=0.22, alias="SCORE_WEIGHT_NOVELTY")
    relevance: float = Field(default=0.18, alias="SCORE_WEIGHT_RELEVANCE")
    distance: float = Field(default=0.18, alias="SCORE_WEIGHT_DISTANCE")
    feasibility: float = Field(default=0.16, alias="SCORE_WEIGHT_FEASIBILITY")
    fun: float = Field(default=0.16, alias="SCORE_WEIGHT_FUN")
    api_fit: float = Field(default=0.10, alias="SCORE_WEIGHT_API_FIT")

    @property
    def local_scan_dirs(self) -> list[str]:
        if not self.local_scan_dirs_raw:
            return []
        return [p.strip() for p in self.local_scan_dirs_raw.split(",") if p.strip()]

    @property
    def resolved_chroma_persist_dir(self) -> Path:
        persist_dir = Path(self.chroma_persist_dir).expanduser()
        if not persist_dir.is_absolute():
            persist_dir = (PROJECT_ROOT / persist_dir).resolve()
        return persist_dir

    @property
    def expanded_local_scan_dirs(self) -> list[str]:
        expanded: list[str] = []
        for entry in self.local_scan_dirs:
            path = Path(entry).expanduser()
            expanded.append(str(path.resolve() if path.exists() else path))
        return expanded

    def score_weights(self) -> dict[str, float]:
        return {
            "novelty": self.novelty,
            "relevance": self.relevance,
            "distance": self.distance,
            "feasibility": self.feasibility,
            "fun": self.fun,
            "api_fit": self.api_fit,
        }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
