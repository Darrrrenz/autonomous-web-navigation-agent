from pathlib import Path
from playwright.async_api import async_playwright, Browser, Page, Playwright

from agent.schema import BrowserAction


DEFAULT_VIEWPORT = {"width": 1440, "height": 900}


async def wait_for_page_ready(page: Page, timeout_ms: int = 5000) -> None:
    try:
        await page.wait_for_load_state("networkidle", timeout=timeout_ms)
    except Exception:
        pass

    await page.wait_for_timeout(500)


async def start_browser(headless: bool = False) -> tuple[Playwright, Browser, Page]:
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=headless)
    page = await browser.new_page(viewport=DEFAULT_VIEWPORT)
    return playwright, browser, page


async def open_start_url(page: Page, url: str = "https://github.com") -> None:
    await page.goto(url)
    await wait_for_page_ready(page)


async def take_screenshot(page: Page, output_path: str | Path) -> str:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    await page.screenshot(path=str(output_path), full_page=False)
    return str(output_path)


async def get_visible_text(page: Page) -> str:
    return await page.locator("body").inner_text()


async def execute_action(page: Page, action: BrowserAction) -> None:
    if action.type == "click":
        click_x = int((action.x1 + action.x2) / 2)
        click_y = int((action.y1 + action.y2) / 2)
        await page.mouse.click(click_x, click_y)

    elif action.type == "type":
        await page.keyboard.type(action.text)

    elif action.type == "press":
        await page.keyboard.press(action.key)

    elif action.type == "scroll":
        amount = action.amount or 600
        dy = -amount if action.direction == "up" else amount
        await page.mouse.wheel(0, dy)

    elif action.type == "wait":
        await page.wait_for_timeout(action.ms or 1000)

    elif action.type == "back":
        await page.go_back()

    elif action.type == "goto":
        await page.goto(action.url)

    else:
        raise ValueError(f"Action '{action.type}' is not an executable action.")

    await wait_for_page_ready(page)


async def close_browser(playwright: Playwright, browser: Browser) -> None:
    await browser.close()
    await playwright.stop()