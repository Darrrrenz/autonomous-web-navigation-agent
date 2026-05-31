import asyncio
from pathlib import Path

from agent.browser import (
    start_browser,
    open_start_url,
    take_screenshot,
    get_visible_text,
    close_browser,
)
from agent.schema import AgentDecision


async def main() -> None:
    output_dir = Path("outputs/smoke_test")
    screenshot_path = output_dir / "github_home.png"

    playwright, browser, page = await start_browser(headless=False)

    try:
        await open_start_url(page, "https://github.com")

        saved_path = await take_screenshot(page, screenshot_path)
        print(f"Screenshot saved to: {saved_path}")

        page_text = await get_visible_text(page)
        print("Visible page text preview:")
        print(page_text[:300])

    finally:
        await close_browser(playwright, browser)


if __name__ == "__main__":
    asyncio.run(main())