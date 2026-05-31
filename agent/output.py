import json
from typing import Any

from agent.models.base import ModelClient


def build_final_output_prompt(
    user_task: str,
    extraction_history: list[dict[str, Any]],
) -> str:
    return f"""
    You are generating the final output for an autonomous GitHub navigation task.

    User task:
    {user_task}

    Extraction history:
    {json.dumps(extraction_history, indent=2, ensure_ascii=False)}

    Return valid JSON only. Do not include markdown fences.

    Use the extraction history to produce one concise final result.
    Ignore duplicate, failed, irrelevant, or low-value extraction entries.
    Do not include raw page text or the full extraction history.

    Return this exact schema:
    {{
        "task": "",
        "status": "success",
        "result": {{}},
        "limitations": []
    }}

    Field rules:
    - task: copy or briefly restate the user task.
    - status: one of "success", "partial", or "failed".
    - result: clean task-specific structured JSON containing the final answer data.
    - limitations: important missing, uncertain, truncated, or not visible information, or [].
    - Use "success" only if the task was answered well enough.
    - Use "partial" if useful information was found but some important requested details are missing.
    - Use "failed" if the extracted information is not enough to answer the task.
    - Keep the final output concise.
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
        raise ValueError(
            "Final output generation returned invalid JSON. "
            f"JSON error: {e}. "
            f"Raw response preview: {raw_response[:1000]}"
        ) from e


def build_final_output(
    model_client: ModelClient,
    user_task: str,
    extraction_history: list[dict[str, Any]],
) -> dict[str, Any]:
    if not extraction_history:
        return {
            "task": user_task,
            "status": "failed",
            "result": {},
            "limitations": ["No extraction result was available."],
        }

    prompt = build_final_output_prompt(
        user_task=user_task,
        extraction_history=extraction_history,
    )
    raw_response = model_client.extract_json(prompt)
    return _parse_json_response(raw_response)