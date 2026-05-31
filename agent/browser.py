from pathlib import Path
from playwright.async_api import async_playwright, Browser, Page, Playwright


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


async def close_browser(playwright: Playwright, browser: Browser) -> None:
    await browser.close()
    await playwright.stop()