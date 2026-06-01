import json
from typing import Any

from agent.models.base import ModelClient


def build_extraction_prompt(
    visible_text: str,
    user_task: str,
) -> str:
    return f"""
    You are extracting useful information from the current GitHub page.

    User task:
    {user_task}

    Visible page text:
    {visible_text}

    Return valid JSON only. Do not include markdown fences.
    Extract only useful information from this page for the user task.
    Do not copy long raw page text. Summarize the information if possible.

    Return this exact schema:
    {{
        "content": "",
        "data": {{}},
        "notes": []
    }}

    Field rules:
    - content: concise summary of useful information found on this page.
    - data: task-specific structured data found on this page.
    - notes: short notes about missing, uncertain, truncated, or not visible information.
    - Keep content concise.
    - If this page has no useful information, say so clearly in content and keep data mostly empty.
    - Make sure the response is valid JSON that can be parsed by json.loads().
    """


def _strip_markdown_fences(raw_response: str) -> str:
    text = raw_response.strip()

    if text.startswith("```json"):
        text = text.removeprefix("```json").strip()
    elif text.startswith("```"):
        text = text.removeprefix("```").strip()

    if text.endswith("```"):
        text = text.removesuffix("```").strip()

    return text


def _parse_json_response(raw_response: str) -> dict[str, Any]:
    text = _strip_markdown_fences(raw_response)

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Extractor returned invalid JSON. Error: {e}.") from e


def extract_page_info(
    model_client: ModelClient,
    visible_text: str,
    user_task: str,
) -> dict[str, Any]:
    prompt = build_extraction_prompt(
        visible_text=visible_text,
        user_task=user_task,
    )
    raw_response = model_client.extract_json(prompt)
    return _parse_json_response(raw_response)