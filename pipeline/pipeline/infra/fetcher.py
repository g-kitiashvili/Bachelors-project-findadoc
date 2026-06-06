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
