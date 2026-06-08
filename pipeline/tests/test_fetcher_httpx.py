import time

import httpx
import pytest

from pipeline.infra.fetcher import HttpxFetcher, FetchError

CHROME_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


def test_httpx_fetcher_sends_generic_chrome_ua(httpx_mock):
    httpx_mock.add_response(url="https://example.test/p", html="<html>ok</html>")
    f = HttpxFetcher(rate_per_sec=10.0)
    body = f.get("https://example.test/p")
    assert body == "<html>ok</html>"
    requests = httpx_mock.get_requests()
    assert requests[0].headers["User-Agent"] == CHROME_UA


def test_httpx_fetcher_raises_fetcherror_on_4xx(httpx_mock):
    httpx_mock.add_response(url="https://example.test/p", status_code=404)
    f = HttpxFetcher(rate_per_sec=10.0)
    with pytest.raises(FetchError) as ei:
        f.get("https://example.test/p")
    assert ei.value.status_code == 404


def test_httpx_fetcher_retries_then_succeeds_on_5xx(httpx_mock):
    httpx_mock.add_response(url="https://example.test/p", status_code=500)
    httpx_mock.add_response(url="https://example.test/p", status_code=500)
    httpx_mock.add_response(url="https://example.test/p", html="<html>finally</html>")
    f = HttpxFetcher(rate_per_sec=100.0)
    body = f.get("https://example.test/p")
    assert body == "<html>finally</html>"
    assert len(httpx_mock.get_requests()) == 3


def test_httpx_fetcher_raises_after_exhausting_retries(httpx_mock):
    for _ in range(3):
        httpx_mock.add_response(url="https://example.test/p", status_code=503)
    f = HttpxFetcher(rate_per_sec=100.0)
    with pytest.raises(FetchError):
        f.get("https://example.test/p")


def test_httpx_fetcher_rate_limits_serial_calls(httpx_mock):
    httpx_mock.add_response(url="https://example.test/a", html="a")
    httpx_mock.add_response(url="https://example.test/b", html="b")
    f = HttpxFetcher(rate_per_sec=5.0)  # → 200 ms min gap
    t0 = time.monotonic()
    f.get("https://example.test/a")
    f.get("https://example.test/b")
    elapsed = time.monotonic() - t0
    assert elapsed >= 0.18  # allow a little slack
