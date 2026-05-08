"""HTTP fetch layer — rate-limited, retried, anonymous.

See project_scraping_policy.md: no robots.txt, no identifying UA.
Rate limits exist purely for detection-avoidance.
"""

from __future__ import annotations

import time
from threading import Lock
from typing import Protocol

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential


CHROME_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


class FetchError(Exception):
    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class Fetcher(Protocol):
    def get(self, url: str) -> str: ...


class _RateLimiter:
    def __init__(self, rate_per_sec: float) -> None:
        if rate_per_sec <= 0:
            raise ValueError("rate_per_sec must be > 0")
        self._min_gap = 1.0 / rate_per_sec
        self._lock = Lock()
        self._last = 0.0

    def wait(self) -> None:
        with self._lock:
            now = time.monotonic()
            sleep_for = self._min_gap - (now - self._last)
            if sleep_for > 0:
                time.sleep(sleep_for)
            self._last = time.monotonic()


class _TransientHttpError(Exception):
    """Internal — triggers tenacity retry."""


class HttpxFetcher:
    def __init__(self, rate_per_sec: float = 1.0, timeout_s: float = 15.0) -> None:
        self._rate = _RateLimiter(rate_per_sec)
        self._client = httpx.Client(
            headers={"User-Agent": CHROME_UA},
            timeout=timeout_s,
            follow_redirects=True,
        )

    def get(self, url: str) -> str:
        try:
            return self._get_with_retry(url)
        except _TransientHttpError as e:
            raise FetchError(str(e), status_code=None) from e

    def post(self, url: str, data: dict[str, object], headers: dict[str, str] | None = None) -> str:
        try:
            return self._post_with_retry(url, data, headers)
        except _TransientHttpError as e:
            raise FetchError(str(e), status_code=None) from e

    @retry(
        retry=retry_if_exception_type(_TransientHttpError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        reraise=True,
    )
    def _get_with_retry(self, url: str) -> str:
        self._rate.wait()
        try:
            response = self._client.get(url)
        except (httpx.TimeoutException, httpx.TransportError) as e:
            raise _TransientHttpError(f"transport error: {e}") from e
        return self._body(response)

    @retry(
        retry=retry_if_exception_type(_TransientHttpError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        reraise=True,
    )
    def _post_with_retry(self, url: str, data: dict[str, object], headers: dict[str, str] | None) -> str:
        self._rate.wait()
        try:
            response = self._client.post(url, data=data, headers=headers)
        except (httpx.TimeoutException, httpx.TransportError) as e:
            raise _TransientHttpError(f"transport error: {e}") from e
        return self._body(response)

    @staticmethod
    def _body(response: httpx.Response) -> str:
        if 500 <= response.status_code < 600:
            raise _TransientHttpError(f"server error {response.status_code}")
        if 400 <= response.status_code < 500:
            raise FetchError(f"client error {response.status_code}", status_code=response.status_code)
        return response.text

    def close(self) -> None:
        self._client.close()


import asyncio

from playwright.async_api import async_playwright
from playwright_stealth import Stealth


class PlaywrightFetcher:
    """Playwright-based fetcher for sites that need a real browser.

    Set `headless=False, stealth=True, cf_wait_ms=8000` for Cloudflare-protected
    sites like Aversi. In production this runs inside the Playwright Docker base
    image which provides Xvfb, so `headless=False` does NOT show a visible window
    on the host.
    """

    def __init__(
        self,
        rate_per_sec: float = 0.5,
        *,
        headless: bool = True,
        stealth: bool = True,
        timeout_s: float = 30.0,
        cf_wait_ms: int = 0,
    ) -> None:
        self._rate = _RateLimiter(rate_per_sec)
        self._headless = headless
        self._stealth = stealth
        self._timeout_ms = int(timeout_s * 1000)
        self._cf_wait_ms = cf_wait_ms

    def get(self, url: str) -> str:
        self._rate.wait()
        return asyncio.run(self._get_async(url))

    async def _get_async(self, url: str) -> str:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self._headless)
            try:
                context = await browser.new_context()
                if self._stealth:
                    await Stealth().apply_stealth_async(context)
                page = await context.new_page()
                response = await page.goto(url, wait_until="domcontentloaded", timeout=self._timeout_ms)
                if response is None:
                    raise FetchError(f"no response for {url}")
                status = response.status
                if 400 <= status < 500:
                    raise FetchError(f"client error {status}", status_code=status)
                if 500 <= status < 600:
                    raise FetchError(f"server error {status}", status_code=status)

                # Give Cloudflare's JS challenge time to auto-solve, if configured.
                if self._cf_wait_ms > 0:
                    await page.wait_for_timeout(self._cf_wait_ms)

                title = await page.title()
                content = await page.content()
                if "Just a moment" in title or "cf-challenge" in content:
                    raise FetchError("cloudflare challenge unresolved", status_code=403)
                return content
            finally:
                await browser.close()
