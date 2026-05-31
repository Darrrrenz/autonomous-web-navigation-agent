import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv


@dataclass
class ModelConfig:
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.0
    max_tokens: Optional[int] = None
    timeout: int = 30
    max_retries: int = 3


def load_model_config() -> ModelConfig:
    load_dotenv()
    max_tokens_raw = os.getenv("MODEL_MAX_TOKENS")
    return ModelConfig(
        model=os.getenv("MODEL_NAME", "gpt-4o"),
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("BASE_URL") or None,
        temperature=float(os.getenv("MODEL_TEMPERATURE", "0")),
        max_tokens=int(max_tokens_raw) if max_tokens_raw else None,
        timeout=int(os.getenv("MODEL_TIMEOUT", "30")),
        max_retries=int(os.getenv("MODEL_MAX_RETRIES", "3")),
    )