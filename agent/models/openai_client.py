import base64
from pathlib import Path
from typing import Any

from openai import OpenAI

from agent.models.config import ModelConfig, load_model_config
from agent.models.base import ModelClient


class OpenAIModelClient(ModelClient):
    def __init__(self, config: ModelConfig | None = None):
        self.config = config or load_model_config()

        if not self.config.api_key:
            raise ValueError("OPENAI_API_KEY is empty.")

        self.client = OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            max_retries=self.config.max_retries,
        )

    def _encode_image(self, image_path: Path) -> str:
        with image_path.open("rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def _build_request_args(self, messages: list[dict[str, Any]]) -> dict[str, Any]:
        request_args: dict[str, Any] = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
        }

        if self.config.max_tokens is not None:
            request_args["max_tokens"] = self.config.max_tokens

        return request_args

    def decide_action(self, prompt: str, screenshot_path: Path) -> str:
        image_b64 = self._encode_image(screenshot_path)
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a vision-based browser navigation agent. Return valid JSON only. Do not include markdown."
                ),
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_b64}"
                        },
                    },
                ],
            },
        ]
        response = self.client.chat.completions.create(
            **self._build_request_args(messages)
        )
        content = response.choices[0].message.content

        if content is None:
            raise ValueError("OpenAI response content is empty.")

        return content

    def extract_json(self, prompt: str) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "You extract structured data from text. Return valid JSON only. Do not include markdown."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]
        response = self.client.chat.completions.create(
            **self._build_request_args(messages)
        )
        content = response.choices[0].message.content

        if content is None:
            raise ValueError("OpenAI response content is empty.")

        return content