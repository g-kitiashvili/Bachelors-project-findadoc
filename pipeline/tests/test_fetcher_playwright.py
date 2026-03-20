import contextlib
import http.server
import socketserver
import threading

import pytest

from pipeline.core.fetcher import PlaywrightFetcher


def test_playwright_fetcher_constructs_with_defaults():
    f = PlaywrightFetcher(rate_per_sec=0.5)
    assert f._rate._min_gap == pytest.approx(2.0)
    assert f._headless is True
    assert f._stealth is True
    assert f._cf_wait_ms == 0


def test_playwright_fetcher_construct_overrides():
    f = PlaywrightFetcher(rate_per_sec=1.0, headless=False, stealth=False, cf_wait_ms=8000)
    assert f._headless is False
    assert f._stealth is False
    assert f._cf_wait_ms == 8000


@pytest.mark.slow
def test_playwright_fetcher_fetches_localhost_static_page(tmp_path):
    page = tmp_path / "page.html"
    page.write_text("<html><body><h1>hello playwright</h1></body></html>", encoding="utf-8")

    handler = http.server.SimpleHTTPRequestHandler
    with contextlib.chdir(tmp_path):
        with socketserver.TCPServer(("127.0.0.1", 0), handler) as httpd:
            port = httpd.server_address[1]
            t = threading.Thread(target=httpd.serve_forever, daemon=True)
            t.start()
            try:
                f = PlaywrightFetcher(rate_per_sec=10.0, headless=True, stealth=False)
                html = f.get(f"http://127.0.0.1:{port}/page.html")
                assert "hello playwright" in html
            finally:
                httpd.shutdown()
