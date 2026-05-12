"""Yahoo Finance market data tool with TTLCache."""

import asyncio
from typing import Any

from cachetools import TTLCache
from pydantic import BaseModel

from app.config.constants import MARKET_CACHE_MAXSIZE, MARKET_CACHE_TTL
from app.utils.errors import MarketAPIError
from app.utils.logger import setup_logger

logger = setup_logger("tools.market")

market_cache: TTLCache = TTLCache(maxsize=MARKET_CACHE_MAXSIZE, ttl=MARKET_CACHE_TTL)


class TickerList(BaseModel):
    tickers: list[str]


def _fetch_market_data_sync(symbol: str) -> dict:
    """Synchronous yfinance call. Wrapped by asyncio.to_thread."""
    import yfinance as yf

    ticker = yf.Ticker(symbol)
    info = ticker.info

    if not info or info.get("regularMarketPrice") is None and info.get("currentPrice") is None:
        hist = ticker.history(period="5d")
        if hist.empty:
            raise MarketAPIError(f"No market data found for symbol: {symbol}")
        current_price = float(hist["Close"].iloc[-1])
        previous_close = float(hist["Close"].iloc[-2]) if len(hist) > 1 else current_price
    else:
        current_price = info.get("currentPrice") or info.get("regularMarketPrice") or 0.0
        previous_close = info.get("previousClose") or info.get("regularMarketPreviousClose") or current_price

    change = round(current_price - previous_close, 2)
    change_pct = round((change / previous_close) * 100, 2) if previous_close else 0.0

    trend = "bullish" if change > 0 else ("bearish" if change < 0 else "neutral")

    market_cap = info.get("marketCap")
    if market_cap:
        if market_cap >= 1e12:
            market_cap_str = f"{market_cap / 1e12:.2f}T"
        elif market_cap >= 1e9:
            market_cap_str = f"{market_cap / 1e9:.2f}B"
        else:
            market_cap_str = f"{market_cap / 1e6:.2f}M"
    else:
        market_cap_str = "N/A"

    volume = info.get("volume") or info.get("regularMarketVolume")
    if volume:
        if volume >= 1e9:
            volume_str = f"{volume / 1e9:.2f}B"
        elif volume >= 1e6:
            volume_str = f"{volume / 1e6:.2f}M"
        else:
            volume_str = str(volume)
    else:
        volume_str = "N/A"

    hist_30d = ticker.history(period="30d")
    chart_data = {"7d": [], "30d": []}

    if not hist_30d.empty:
        hist_data = hist_30d.reset_index()
        for _, row in hist_data.iterrows():
            date_str = row["Date"].strftime("%Y-%m-%d") if hasattr(row["Date"], "strftime") else str(row["Date"])[:10]
            close_val = float(row["Close"])
            entry = {"date": date_str, "close": round(close_val, 2)}
            chart_data["30d"].append(entry)

        chart_data["7d"] = chart_data["30d"][-7:] if len(chart_data["30d"]) >= 7 else chart_data["30d"]

    return {
        "symbol": symbol,
        "price": round(current_price, 2),
        "change": change,
        "change_pct": change_pct,
        "trend": trend,
        "market_metrics": {
            "market_cap": market_cap_str,
            "pe_ratio": info.get("trailingPE") or info.get("forwardPE"),
            "volume": volume_str,
        },
        "chart_data": chart_data,
    }


async def fetch_market_data(symbol: str) -> dict[str, Any]:
    """Fetch and normalize market data for a single symbol."""
    cache_key = symbol.upper()
    if cache_key in market_cache:
        logger.info(f"Cache hit for {cache_key}")
        return market_cache[cache_key]

    logger.info(f"Fetching market data for {cache_key}")
    try:
        result = await asyncio.to_thread(_fetch_market_data_sync, cache_key)
        market_cache[cache_key] = result
        return result
    except MarketAPIError:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch data for {cache_key}: {e}")
        raise MarketAPIError(f"Failed to retrieve market data for {cache_key}: {e}")


async def fetch_all_market_data(tickers: list[str]) -> dict[str, dict]:
    """Fetch data for multiple tickers in parallel."""
    results_list = await asyncio.gather(
        *[fetch_market_data(t) for t in tickers],
        return_exceptions=True,
    )
    result_dict = {}
    for ticker, res in zip(tickers, results_list):
        if isinstance(res, Exception):
            logger.error(f"Error fetching {ticker}: {res}")
            raise MarketAPIError(f"Failed to retrieve market data for {ticker}: {res}")
        result_dict[ticker.upper()] = res
    return result_dict


async def extract_tickers(query: str, model) -> list[str]:
    """Extract ticker symbols from query via LLM function_calling."""
    try:
        structured_llm = model.with_structured_output(TickerList, method="function_calling")
        result = await structured_llm.ainvoke(
            f"Extract all stock ticker symbols from this query. Only return valid ticker symbols (e.g., TSLA, AAPL, NVDA). Return empty list if none found.\n\nQuery: {query}"
        )
        if result is None:
            return []
        tickers = result.tickers if isinstance(result, TickerList) else (result.get("tickers", []) if isinstance(result, dict) else [])
        if isinstance(tickers, list):
            return [t.upper().strip() for t in tickers if t and isinstance(t, str)]
        return []
    except Exception as e:
        logger.error(f"Ticker extraction failed: {e}")
        return []
