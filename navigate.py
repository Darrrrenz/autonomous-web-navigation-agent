import asyncio
import json
from pathlib import Path
from typing import Any
from pydantic import ValidationError

from agent.browser import (
    start_browser,
    open_start_url,
    take_screenshot,
    execute_action,
    close_browser,
    get_visible_text,
)
from agent.cli import DEFAULT_REPO, build_user_task, parse_args
from agent.extractor import extract_page_info
from agent.models.openai_client import OpenAIModelClient
from agent.output import build_final_output
from agent.vlm_agent import decide_next_action


def make_output_dir() -> Path:
    output_dir = Path("outputs/multi_step_agent_test")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


async def perform_extract(
    page,
    step: int,
    model_client: OpenAIModelClient,
    user_task: str,
) -> dict[str, Any]:
    visible_text = await get_visible_text(page)
    extracted_data = extract_page_info(
        model_client=model_client,
        visible_text=visible_text,
        user_task=user_task,
    )
    return {
        "step": step,
        "source": "visible_page_text",
        "extracted_data": extracted_data,
    }


async def main() -> None:
    args = parse_args()
    output_dir = make_output_dir()
    screenshots_dir = output_dir / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    run_log_path = output_dir / "run_log.json"
    extracted_path = output_dir / "extracted_information.json"
    final_output_path = output_dir / "final_output.json"

    user_task = build_user_task(args)
    model_client = OpenAIModelClient()
    navigation_steps = 0
    model_failures = 0
    history: list[dict[str, Any]] = []
    extraction_history: list[dict[str, Any]] = []
    previous_expected_result: str | None = None

    final_status = "unknown"
    final_reason = ""

    playwright, browser, page = await start_browser(headless=False)

    try:
        await open_start_url(page, args.start_url)

        while navigation_steps < args.max_steps:
            step = navigation_steps + 1
            print(f"\n===== Step {step} =====")
            screenshot_path = await take_screenshot(
                page,
                screenshots_dir / f"step_{step:03d}.png",
            )

            try:
                decision = decide_next_action(
                    model_client=model_client,
                    screenshot_path=Path(screenshot_path),
                    user_task=user_task,
                    recent_history=history[-5:],
                    previous_expected_result=previous_expected_result,
                    extraction_history=extraction_history[-5:],
                )
            except (json.JSONDecodeError, ValidationError, ValueError) as e:
                model_failures += 1
                history.append(
                    {
                        "event": "model_parse_or_validation_error",
                        "model_failures": model_failures,
                        "error": str(e),
                        "screenshot": screenshot_path,
                    }
                )
                print(f"Model output error {model_failures}/{args.max_model_failures}: {e}")

                if model_failures >= args.max_model_failures:
                    final_status = "failed"
                    final_reason = "Too many model parse or validation failures."
                    break

                continue

            navigation_steps += 1
            action = decision.next_action

            print(decision.model_dump_json(indent=2))

            history_item = {
                "step": navigation_steps,
                "screenshot": screenshot_path,
                "previous_action_success": decision.previous_action_success,
                "error_explanation": decision.error_explanation,
                "action": action.model_dump(exclude_none=True),
                "expected_result": decision.expected_result,
                "confidence": decision.confidence,
            }

            history.append(history_item)
            previous_expected_result = decision.expected_result

            if action.type == "extract":
                try:
                    extracted = await perform_extract(
                        page=page,
                        step=navigation_steps,
                        model_client=model_client,
                        user_task=user_task,
                    )
                except Exception as e:
                    extracted = {
                        "step": navigation_steps,
                        "source": "visible_page_text",
                        "error": "extraction_failed",
                        "error_message": str(e),
                        "extracted_data": {
                            "content": "Extraction failed.",
                            "data": {},
                            "notes": [
                                "The extractor failed to return valid structured data."
                            ],
                        },
                    }
                    print(f"Extraction failed at step {navigation_steps}: {e}")

                extraction_history.append(extracted)
                print(f"Extraction recorded at step {navigation_steps}.")
                continue

            if action.type == "done":
                final_status = "success"
                final_reason = "Model reported task completed."
                break

            if action.type == "fail":
                final_status = "failed"
                final_reason = decision.error_explanation or "Model returned fail."
                break

            await execute_action(page, action)

        else:
            final_status = "failed"
            final_reason = "Maximum navigation steps reached."

        final_screenshot = await take_screenshot(
            page,
            screenshots_dir / "final.png",
        )

        try:
            final_output = build_final_output(
                model_client=model_client,
                user_task=user_task,
                extraction_history=extraction_history,
            )
        except Exception as e:
            final_output = {
                "task": user_task,
                "status": "failed",
                "result": {},
                "limitations": [
                    f"Failed to generate final output: {e}"
                ],
            }

        with extracted_path.open("w", encoding="utf-8") as f:
            json.dump(extraction_history, f, indent=2, ensure_ascii=False)

        with final_output_path.open("w", encoding="utf-8") as f:
            json.dump(final_output, f, indent=2, ensure_ascii=False)

        with run_log_path.open("w", encoding="utf-8") as f:
            json.dump(
                {
                    "task": user_task,
                    "start_url": args.start_url,
                    "repo": args.repo or DEFAULT_REPO,
                    "max_steps": args.max_steps,
                    "max_model_failures": args.max_model_failures,
                    "navigation_steps": navigation_steps,
                    "model_failures": model_failures,
                    "final_status": final_status,
                    "final_reason": final_reason,
                    "final_screenshot": final_screenshot,
                    "history": history,
                    "extraction_history": extraction_history,
                    "final_output": final_output,
                },
                f,
                indent=2,
                ensure_ascii=False,
            )

        print(f"\nFinal status: {final_status}")
        print(f"Final reason: {final_reason}")
        print(f"Run log saved to: {run_log_path}")
        print(f"Extracted information saved to: {extracted_path}")
        print(f"Final output saved to: {final_output_path}")
        print(f"Final screenshot saved to: {final_screenshot}")

    finally:
        await close_browser(playwright, browser)


if __name__ == "__main__":
    asyncio.run(main())