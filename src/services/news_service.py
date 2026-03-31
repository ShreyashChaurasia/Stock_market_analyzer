import re
from collections import Counter
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from typing import Any
from urllib.parse import urlencode
import xml.etree.ElementTree as ET

import httpx

from src.core.config import settings
from src.core.logger import get_logger
from src.utils.cache import cache

logger = get_logger(__name__)


class NewsService:
    """Fetch and normalize stock-market news from external providers."""

    GNEWS_SEARCH_URL = "https://gnews.io/api/v4/search"
    NEWSAPI_EVERYTHING_URL = "https://newsapi.org/v2/everything"
    GOOGLE_NEWS_RSS_URL = "https://news.google.com/rss/search"

    MARKET_QUERIES = {
        "ALL": "stock market OR equities OR earnings OR wall street OR nifty OR sensex",
        "US": "us stock market OR wall street OR nasdaq OR dow jones OR earnings",
        "INDIA": "india stock market OR nse OR bse OR nifty OR sensex",
    }

    GOOGLE_NEWS_LOCALES = {
        "ALL": {"hl": "en-US", "gl": "US", "ceid": "US:en"},
        "US": {"hl": "en-US", "gl": "US", "ceid": "US:en"},
        "INDIA": {"hl": "en-IN", "gl": "IN", "ceid": "IN:en"},
    }

    NOISE_TICKERS = {
        "A",
        "AI",
        "CEO",
        "EPS",
        "ETF",
        "GDP",
        "IPO",
        "IT",
        "OR",
        "THE",
        "USA",
        "USD",
    }

    def __init__(self) -> None:
        self.provider = (settings.NEWS_PROVIDER or "gnews").lower()
        self._universe_tickers = {ticker.upper() for ticker in settings.HIGH_CONFIDENCE_UNIVERSE}

    @staticmethod
    def _normalize_market(market: str | None) -> str:
        normalized = (market or "ALL").strip().upper()
        if normalized not in {"ALL", "US", "INDIA"}:
            return "ALL"
        return normalized

    @staticmethod
    def _infer_market_from_ticker(ticker: str) -> str:
        if ticker.endswith((".NS", ".BO")):
            return "INDIA"
        return "US"

    @staticmethod
    def _cache_key(*parts: str) -> str:
        joined = ":".join(parts)
        return f"news:{joined}"

    def _extract_tickers(self, text: str, forced_ticker: str | None = None) -> list[str]:
        symbols = set()
        if forced_ticker:
            symbols.add(forced_ticker.upper())

        if not text:
            return sorted(symbols)

        matches = re.findall(r"\b[A-Z]{1,5}(?:\.(?:NS|BO))?\b", text.upper())
        for token in matches:
            if token in self.NOISE_TICKERS:
                continue
            if token in self._universe_tickers or token.endswith((".NS", ".BO")):
                symbols.add(token)

        return sorted(symbols)

    def _normalize_article(
        self,
        raw: dict[str, Any],
        *,
        source_name: str,
        market: str,
        forced_ticker: str | None = None,
    ) -> dict[str, Any] | None:
        title = (raw.get("title") or "").strip()
        url = (raw.get("url") or "").strip()
        if not title or not url:
            return None

        description = (raw.get("description") or "").strip() or None
        image_url = (raw.get("image") or raw.get("urlToImage") or "").strip() or None
        published_at = (
            raw.get("publishedAt")
            or raw.get("published_at")
            or datetime.utcnow().isoformat()
        )

        article_source = raw.get("source")
        if isinstance(article_source, dict):
            source_label = article_source.get("name") or source_name
        elif isinstance(article_source, str) and article_source.strip():
            source_label = article_source.strip()
        else:
            source_label = source_name

        text_blob = f"{title} {description or ''}"
        tickers = self._extract_tickers(text_blob, forced_ticker=forced_ticker)

        return {
            "title": title,
            "description": description,
            "url": url,
            "source": source_label,
            "published_at": str(published_at),
            "image_url": image_url,
            "tickers": tickers,
            "market": market,
        }

    def _fetch_from_gnews(self, query: str, limit: int, market: str) -> list[dict[str, Any]]:
        if not settings.GNEWS_API_KEY:
            logger.warning("GNews API key is not configured; skipping GNews fetch.")
            return []

        params = {
            "q": query,
            "lang": "en",
            "max": max(1, min(limit, 50)),
            "sortby": "publishedAt",
            "token": settings.GNEWS_API_KEY,
        }

        if market == "US":
            params["country"] = "us"
        elif market == "INDIA":
            params["country"] = "in"

        response = httpx.get(self.GNEWS_SEARCH_URL, params=params, timeout=12.0)
        response.raise_for_status()
        payload = response.json()
        articles = payload.get("articles", [])

        normalized: list[dict[str, Any]] = []
        for article in articles:
            item = self._normalize_article(article, source_name="GNews", market=market)
            if item:
                normalized.append(item)

        return normalized

    def _fetch_from_newsapi(self, query: str, limit: int, market: str) -> list[dict[str, Any]]:
        if not settings.NEWSAPI_API_KEY:
            logger.warning("NewsAPI API key is not configured; skipping NewsAPI fetch.")
            return []

        params = {
            "q": query,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": max(1, min(limit, 100)),
            "apiKey": settings.NEWSAPI_API_KEY,
        }

        if market == "US":
            params["domains"] = "wsj.com,cnbc.com,bloomberg.com,reuters.com"
        elif market == "INDIA":
            params["domains"] = "economictimes.indiatimes.com,moneycontrol.com,business-standard.com"

        response = httpx.get(self.NEWSAPI_EVERYTHING_URL, params=params, timeout=12.0)
        response.raise_for_status()
        payload = response.json()
        articles = payload.get("articles", [])

        normalized: list[dict[str, Any]] = []
        for article in articles:
            item = self._normalize_article(article, source_name="NewsAPI", market=market)
            if item:
                normalized.append(item)

        return normalized

    @staticmethod
    def _strip_html(value: str | None) -> str | None:
        if not value:
            return None

        text = re.sub(r"<[^>]+>", " ", value)
        text = unescape(re.sub(r"\s+", " ", text)).strip()
        return text or None

    def _fetch_from_google_news_rss(
        self,
        query: str,
        limit: int,
        market: str,
        *,
        forced_ticker: str | None = None,
    ) -> list[dict[str, Any]]:
        locale = self.GOOGLE_NEWS_LOCALES.get(market, self.GOOGLE_NEWS_LOCALES["ALL"])
        url = f"{self.GOOGLE_NEWS_RSS_URL}?{urlencode({'q': query, **locale})}"

        response = httpx.get(url, timeout=12.0)
        response.raise_for_status()

        root = ET.fromstring(response.text)
        normalized: list[dict[str, Any]] = []

        for article in root.findall("./channel/item"):
            source_label = (article.findtext("source") or "Google News").strip()
            title = unescape((article.findtext("title") or "").strip())
            if source_label and title.endswith(f" - {source_label}"):
                title = title[: -(len(source_label) + 3)].strip()

            payload = {
                "title": title,
                "description": self._strip_html(article.findtext("description")),
                "url": unescape((article.findtext("link") or "").strip()),
                "source": source_label,
                "publishedAt": (article.findtext("pubDate") or "").strip(),
            }
            item = self._normalize_article(
                payload,
                source_name="Google News RSS",
                market=market,
                forced_ticker=forced_ticker,
            )
            if item:
                normalized.append(item)

            if len(normalized) >= limit:
                break

        return normalized

    def _fetch_news(
        self,
        query: str,
        limit: int,
        market: str,
        *,
        forced_ticker: str | None = None,
    ) -> list[dict[str, Any]]:
        provider = self.provider
        primary_chain = (
            [("newsapi", self._fetch_from_newsapi), ("gnews", self._fetch_from_gnews)]
            if provider == "newsapi"
            else [("gnews", self._fetch_from_gnews), ("newsapi", self._fetch_from_newsapi)]
        )
        errors: list[str] = []

        for provider_name, fetcher in primary_chain:
            try:
                news = fetcher(query, limit, market)
                if news:
                    return news
            except Exception as exc:
                logger.warning(
                    "News provider '%s' failed for market '%s' and query '%s': %s",
                    provider_name,
                    market,
                    query,
                    exc,
                )
                errors.append(f"{provider_name}: {exc}")

        try:
            news = self._fetch_from_google_news_rss(
                query,
                limit,
                market,
                forced_ticker=forced_ticker,
            )
            if news:
                logger.info(
                    "Using Google News RSS fallback for market '%s' and query '%s'.",
                    market,
                    query,
                )
                return news
        except Exception as exc:
            logger.warning(
                "Google News RSS fallback failed for market '%s' and query '%s': %s",
                market,
                query,
                exc,
            )
            errors.append(f"google_rss: {exc}")

        if errors:
            logger.error(
                "Failed to fetch news for market '%s' and query '%s' after all providers: %s",
                market,
                query,
                "; ".join(errors),
            )

        return []

    @staticmethod
    def _parse_published_at(value: Any) -> datetime:
        raw = str(value or "").strip()
        if not raw:
            return datetime.min

        try:
            parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            if parsed.tzinfo is not None:
                return parsed.astimezone(timezone.utc).replace(tzinfo=None)
            return parsed
        except ValueError:
            pass

        try:
            parsed = parsedate_to_datetime(raw)
            if parsed.tzinfo is not None:
                return parsed.astimezone(timezone.utc).replace(tzinfo=None)
            return parsed
        except (TypeError, ValueError, IndexError, OverflowError):
            pass

        for parser in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
            try:
                return datetime.strptime(raw[:19], parser)
            except ValueError:
                continue

        return datetime.min

    @staticmethod
    def _resolve_cache_ttl(items: list[Any], default_ttl: int) -> int:
        if items:
            return default_ttl
        return min(default_ttl, 120)

    @classmethod
    def _sort_recent_first(cls, articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return sorted(
            articles,
            key=lambda item: cls._parse_published_at(item.get("published_at")),
            reverse=True,
        )

    @staticmethod
    def _build_stock_queries(ticker: str, market: str) -> list[str]:
        base_symbol = ticker.split(".")[0].strip().upper()

        queries = [
            f'"{ticker}" stock OR shares OR earnings OR guidance',
            f'"{base_symbol}" stock OR "{base_symbol}" shares OR "{base_symbol}" earnings',
        ]

        if market == "INDIA":
            queries.append(
                f'"{base_symbol}" NSE OR "{base_symbol}" BSE OR "{base_symbol}" India stock market'
            )
        else:
            queries.append(
                f'"{base_symbol}" stock market OR "{base_symbol}" NYSE OR "{base_symbol}" NASDAQ'
            )

        queries.append(f'"{base_symbol}" company financial results')

        deduped: list[str] = []
        seen: set[str] = set()
        for query in queries:
            normalized_query = query.strip()
            if not normalized_query or normalized_query in seen:
                continue
            seen.add(normalized_query)
            deduped.append(normalized_query)

        return deduped

    @staticmethod
    def _article_mentions_symbol(
        article: dict[str, Any],
        ticker: str,
        base_symbol: str,
    ) -> bool:
        title = str(article.get("title") or "")
        description = str(article.get("description") or "")
        text_blob = f"{title} {description}".upper()
        return ticker in text_blob or base_symbol in text_blob

    def get_latest_news(self, limit: int | None = None, market: str = "ALL") -> list[dict[str, Any]]:
        bounded_limit = max(1, min(limit or settings.NEWS_DEFAULT_LIMIT, 30))
        normalized_market = self._normalize_market(market)
        query = self.MARKET_QUERIES[normalized_market]

        cache_key = self._cache_key("latest", normalized_market, str(bounded_limit))
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        articles = self._fetch_news(query=query, limit=bounded_limit, market=normalized_market)
        cache.set(cache_key, articles, ttl=self._resolve_cache_ttl(articles, settings.NEWS_CACHE_TTL))
        return articles

    def get_stock_news(self, ticker: str, limit: int | None = None) -> list[dict[str, Any]]:
        normalized_ticker = (ticker or "").strip().upper()
        if not normalized_ticker:
            return []

        bounded_limit = max(1, min(limit or settings.NEWS_DEFAULT_LIMIT, 20))
        market = self._infer_market_from_ticker(normalized_ticker)
        base_symbol = normalized_ticker.split(".")[0].strip().upper()

        cache_key = self._cache_key("stock", normalized_ticker, str(bounded_limit))
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        fetch_limit = max(10, min(bounded_limit * 3, 40))
        articles: list[dict[str, Any]] = []
        for query in self._build_stock_queries(normalized_ticker, market):
            candidate_articles = self._fetch_news(
                query=query,
                limit=fetch_limit,
                market=market,
                forced_ticker=normalized_ticker,
            )
            if candidate_articles:
                articles = candidate_articles
                break

        if not articles:
            latest_pool = self.get_latest_news(limit=max(bounded_limit * 4, 20), market=market)
            articles = [
                article
                for article in latest_pool
                if self._article_mentions_symbol(article, normalized_ticker, base_symbol)
            ]

        normalized_articles: list[dict[str, Any]] = []
        for article in articles:
            item = dict(article)
            tickers = set(item.get("tickers", []))
            tickers.add(normalized_ticker)
            item["tickers"] = sorted(tickers)
            item["market"] = market
            normalized_articles.append(item)

        sorted_articles = self._sort_recent_first(normalized_articles)[:bounded_limit]
        ttl = self._resolve_cache_ttl(sorted_articles, settings.NEWS_CACHE_TTL)
        cache.set(cache_key, sorted_articles, ttl=ttl)
        return sorted_articles

    def get_trending_news(self, limit: int | None = None, market: str = "ALL") -> dict[str, Any]:
        bounded_limit = max(1, min(limit or settings.NEWS_DEFAULT_LIMIT, 20))
        normalized_market = self._normalize_market(market)

        cache_key = self._cache_key("trending", normalized_market, str(bounded_limit))
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        pool_size = max(bounded_limit * 3, 15)
        articles = self.get_latest_news(limit=pool_size, market=normalized_market)

        ticker_counts: Counter[str] = Counter()
        for article in articles:
            for ticker in article.get("tickers", []):
                ticker_counts[ticker] += 1

        trending_tickers = [
            {"ticker": ticker, "mentions": mentions}
            for ticker, mentions in ticker_counts.most_common(bounded_limit)
        ]

        result = {
            "articles": articles[:bounded_limit],
            "trending_tickers": trending_tickers,
            "provider": self.provider,
            "market": normalized_market,
            "generated_at": datetime.utcnow().isoformat(),
        }
        ttl = self._resolve_cache_ttl(result["articles"], settings.NEWS_CACHE_TTL)
        cache.set(cache_key, result, ttl=ttl)
        return result


news_service = NewsService()
