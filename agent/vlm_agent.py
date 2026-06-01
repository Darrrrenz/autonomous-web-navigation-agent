import json
from pathlib import Path

from agent.models.base import ModelClient
from agent.schema import AgentDecision


def build_navigation_prompt(
    user_task: str,
    recent_history: list[dict],
    previous_expected_result: str | None,
    extraction_history: list[dict],
) -> str:
    return f"""
    You are a vision-based browser navigation agent.

    Your job is to complete the user task by looking at the current browser screenshot
    and choosing the next browser action.

    Important rules:
    - Do not use CSS selectors, XPath, class names, ids, hrefs, or hidden DOM structure.
    - Use only the screenshot, recent action history, and extracted page information.
    - First decide whether the most recent action achieved its expected result.
    - Then choose exactly one next action.
    - Return valid JSON only.
    - Do not include markdown fences.
    - Do not include explanations outside JSON.
    - Do not construct or directly navigate to GitHub URLs. Use visible browser interactions such as click, type, press, scroll, wait, and back.

    Coordinate rules:
    - Use pixel coordinates from the current screenshot. The size should be 1440x900.
    - The top-left corner of the screenshot is (0, 0).
    - For click actions, return a bounding box around the visible clickable target.
    - The program will click the center of the bounding box.
    - The bounding box should cover only the intended clickable target.
    - Do not include nearby buttons or unrelated UI elements.
    - If the target is a text input, the bounding box should cover the input field itself.

    Extraction behavior:
    - Use extract when the current page appears to contain information useful for the user task.
    - After extraction, you will receive extracted information in the next prompt.
    - If the latest extracted information has "done": true and "missing" is empty, return done.
    - If "missing" is not empty, continue navigating if there is a reasonable way to find the missing information.
    - If missing information is not visible and there is no reasonable next action, return done only if the main user task has been answered well enough.

    User task:
    {user_task}

    Recent action history:
    {json.dumps(recent_history, indent=2)}

    Previous expected result:
    {previous_expected_result or "None. This is the first step."}

    Previous extracted information:
    {json.dumps(extraction_history, indent=2)}

    Allowed actions:
    1. click: requires x1, y1, x2, y2 as a bounding box around the visible clickable target. The program will click the center of the box.
    2. type: requires text
    3. press: requires key
    4. scroll: requires direction ("up" or "down") and amount
    5. wait: requires ms
    6. back: requires no extra parameters
    7. extract: use when the current page has information useful for the user task
    8. done: use only if the task is completed
    9. fail: use only if no reasonable next action is possible

    Return JSON using exactly this schema:
    {{
    "previous_action_success": true,
    "error_explanation": "",
    "next_action": {{
        "type": "click",
        "reason": "brief reason",
        "x1": 0,
        "y1": 0,
        "x2": 0,
        "y2": 0,
        "text": null,
        "key": null,
        "direction": null,
        "amount": null,
        "ms": null
    }},
    "expected_result": "what should happen after the next action",
    "confidence": 0.0
    }}
    """


def _parse_agent_decision(raw_response: str) -> AgentDecision:
    data = json.loads(raw_response)
    return AgentDecision.model_validate(data)


def decide_next_action(
    model_client: ModelClient,
    screenshot_path: Path,
    user_task: str,
    recent_history: list[dict],
    previous_expected_result: str | None,
    extraction_history: list[dict],
) -> AgentDecision:
    prompt = build_navigation_prompt(
        user_task=user_task,
        recent_history=recent_history,
        previous_expected_result=previous_expected_result,
        extraction_history=extraction_history,
    )
    raw_response = model_client.decide_action(
        prompt=prompt,
        screenshot_path=screenshot_path,
    )
    return _parse_agent_decision(raw_response)