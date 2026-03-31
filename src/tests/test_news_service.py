import pytest

from src.core.config import settings
from src.services.news_service import NewsService
from src.utils.cache import cache


def _sample_article(title: str = "Apple extends rally") -> dict:
    return {
        "title": title,
        "description": "Markets reacted positively to fresh guidance.",
        "url": "https://example.com/apple-rally",
        "source": "Example",
        "published_at": "2026-03-31T09:30:00",
        "image_url": None,
        "tickers": ["AAPL"],
        "market": "US",
    }


@pytest.fixture(autouse=True)
def clear_news_cache():
    cache.clear()
    yield
    cache.clear()


def test_fetch_news_tries_secondary_provider_when_primary_fails(monkeypatch):
    service = NewsService()
    calls: list[str] = []

    def fail_primary(query: str, limit: int, market: str):
        calls.append("gnews")
        raise RuntimeError("provider unavailable")

    def succeed_secondary(query: str, limit: int, market: str):
        calls.append("newsapi")
        return [_sample_article()]

    monkeypatch.setattr(service, "_fetch_from_gnews", fail_primary)
    monkeypatch.setattr(service, "_fetch_from_newsapi", succeed_secondary)
    monkeypatch.setattr(
        service,
        "_fetch_from_google_news_rss",
        lambda query, limit, market, forced_ticker=None: [],
    )

    articles = service._fetch_news(query="AAPL earnings", limit=5, market="US")

    assert len(articles) == 1
    assert calls == ["gnews", "newsapi"]


def test_google_news_rss_normalizes_feed_items(monkeypatch):
    service = NewsService()
    feed = """
    <?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
      <channel>
        <item>
          <title>Apple rallies after earnings beat - Reuters</title>
          <link>https://news.google.com/rss/articles/example</link>
          <pubDate>Mon, 31 Mar 2026 10:00:00 GMT</pubDate>
          <description><![CDATA[<a href="https://news.google.com/rss/articles/example">Apple rallies after earnings beat - Reuters</a>]]></description>
          <source>Reuters</source>
        </item>
      </channel>
    </rss>
    """.strip()

    class DummyResponse:
        def __init__(self, text: str) -> None:
            self.text = text

        def raise_for_status(self) -> None:
            return None

    monkeypatch.setattr(
        "src.services.news_service.httpx.get",
        lambda *args, **kwargs: DummyResponse(feed),
    )

    articles = service._fetch_from_google_news_rss(
        "AAPL earnings",
        5,
        "US",
        forced_ticker="AAPL",
    )

    assert len(articles) == 1
    assert articles[0]["title"] == "Apple rallies after earnings beat"
    assert articles[0]["source"] == "Reuters"
    assert articles[0]["published_at"] == "Mon, 31 Mar 2026 10:00:00 GMT"
    assert articles[0]["tickers"] == ["AAPL"]


def test_get_latest_news_uses_short_ttl_for_empty_results(monkeypatch):
    service = NewsService()
    captured: dict[str, object] = {}

    monkeypatch.setattr("src.services.news_service.cache.get", lambda key: None)
    monkeypatch.setattr(
        "src.services.news_service.cache.set",
        lambda key, value, ttl: captured.update({"ttl": ttl, "value": value}),
    )
    monkeypatch.setattr(
        service,
        "_fetch_news",
        lambda query, limit, market, forced_ticker=None: [],
    )

    articles = service.get_latest_news(limit=5, market="ALL")

    assert articles == []
    assert captured["value"] == []
    assert captured["ttl"] == min(settings.NEWS_CACHE_TTL, 120)


def test_get_trending_news_uses_short_ttl_for_empty_results(monkeypatch):
    service = NewsService()
    captured: dict[str, object] = {}

    monkeypatch.setattr("src.services.news_service.cache.get", lambda key: None)
    monkeypatch.setattr(
        "src.services.news_service.cache.set",
        lambda key, value, ttl: captured.update({"ttl": ttl, "value": value}),
    )
    monkeypatch.setattr(service, "get_latest_news", lambda limit, market: [])

    result = service.get_trending_news(limit=5, market="ALL")

    assert result["articles"] == []
    assert result["trending_tickers"] == []
    assert captured["ttl"] == min(settings.NEWS_CACHE_TTL, 120)
