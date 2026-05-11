#!/usr/bin/env python3
"""
MCP server for querying the marketnews MySQL database.
"""

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import mysql.connector
import os

load_dotenv()

mcp = FastMCP("marketnews")


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 3307)),
        database=os.getenv("DB_NAME", "marketnews"),
        user=os.getenv("DB_USER", "marketnews"),
        password=os.getenv("DB_PASSWORD", "marketnews_pass"),
    )


@mcp.tool()
def search_articles(
    keyword: str = "",
    ticker: str = "",
    source: str = "",
    from_date: str = "",
    to_date: str = "",
    limit: int = 20,
) -> list[dict]:
    """
    Search articles by keyword (title/summary), ticker symbol, source, or date range.
    Dates should be in YYYY-MM-DD format. Returns up to `limit` articles (max 100).
    """
    limit = min(limit, 100)
    conditions = []
    params = []

    if keyword:
        conditions.append("(mn.title LIKE %s OR mn.summary LIKE %s)")
        params += [f"%{keyword}%", f"%{keyword}%"]
    if source:
        conditions.append("mn.source LIKE %s")
        params.append(f"%{source}%")
    if from_date:
        conditions.append("DATE(mn.published_time) >= %s")
        params.append(from_date)
    if to_date:
        conditions.append("DATE(mn.published_time) <= %s")
        params.append(to_date)
    if ticker:
        conditions.append("EXISTS (SELECT 1 FROM ticker_sentiments ts WHERE ts.article_id = mn.id AND ts.ticker = %s)")
        params.append(ticker.upper())

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    query = f"""
        SELECT mn.id, mn.title, mn.source, mn.url, mn.published_time
        FROM market_news mn
        {where}
        ORDER BY mn.published_time DESC
        LIMIT %s
    """
    params.append(limit)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    for row in rows:
        if row.get("published_time"):
            row["published_time"] = str(row["published_time"])
    return rows


@mcp.tool()
def get_article(article_id: int) -> dict:
    """
    Get a single article by ID, including its full summary and all ticker sentiments.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT id, title, summary, url, source, published_time FROM market_news WHERE id = %s",
        (article_id,),
    )
    article = cursor.fetchone()
    if not article:
        cursor.close()
        conn.close()
        return {"error": f"No article found with id {article_id}"}

    article["published_time"] = str(article["published_time"])

    cursor.execute(
        """
        SELECT ticker, sentiment_label, sentiment_score, relevance_score
        FROM ticker_sentiments
        WHERE article_id = %s
        ORDER BY relevance_score DESC
        """,
        (article_id,),
    )
    article["ticker_sentiments"] = cursor.fetchall()
    cursor.close()
    conn.close()
    return article


@mcp.tool()
def get_sentiment_report(
    from_date: str = "",
    to_date: str = "",
    sentiment_label: str = "",
    min_mentions: int = 10,
    limit: int = 30,
) -> list[dict]:
    """
    Get tickers ranked by average sentiment score.
    Optionally filter by date range (YYYY-MM-DD), sentiment_label
    (Bullish, Somewhat-Bullish, Neutral, Somewhat-Bearish, Bearish),
    and minimum number of mentions. Returns up to `limit` tickers.
    """
    limit = min(limit, 100)
    conditions = []
    params = []

    if from_date:
        conditions.append("mn.published_time >= %s")
        params.append(from_date)
    if to_date:
        conditions.append("mn.published_time <= %s")
        params.append(to_date + " 23:59:59")
    if sentiment_label:
        conditions.append("ts.sentiment_label = %s")
        params.append(sentiment_label)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    query = f"""
        SELECT
            ts.ticker,
            COUNT(*) AS total_mentions,
            ROUND(AVG(ts.sentiment_score), 4) AS avg_sentiment_score,
            SUM(CASE WHEN ts.sentiment_label IN ('Bullish','Somewhat-Bullish') THEN 1 ELSE 0 END) AS positive,
            SUM(CASE WHEN ts.sentiment_label = 'Neutral' THEN 1 ELSE 0 END) AS neutral,
            SUM(CASE WHEN ts.sentiment_label IN ('Bearish','Somewhat-Bearish') THEN 1 ELSE 0 END) AS negative
        FROM ticker_sentiments ts
        JOIN market_news mn ON ts.article_id = mn.id
        {where}
        GROUP BY ts.ticker
        HAVING total_mentions >= %s
        ORDER BY avg_sentiment_score DESC
        LIMIT %s
    """
    params += [min_mentions, limit]

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


@mcp.tool()
def get_top_tickers(
    from_date: str = "",
    to_date: str = "",
    order_by: str = "mentions",
    limit: int = 25,
) -> list[dict]:
    """
    Get tickers ranked by total mentions or average sentiment score.
    order_by: 'mentions' or 'score'. Dates in YYYY-MM-DD format.
    """
    limit = min(limit, 100)
    conditions = []
    params = []

    if from_date:
        conditions.append("mn.published_time >= %s")
        params.append(from_date)
    if to_date:
        conditions.append("mn.published_time <= %s")
        params.append(to_date + " 23:59:59")

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    sort = "total_mentions" if order_by == "mentions" else "avg_sentiment_score"
    query = f"""
        SELECT
            ts.ticker,
            COUNT(*) AS total_mentions,
            ROUND(AVG(ts.sentiment_score), 4) AS avg_sentiment_score,
            SUM(CASE WHEN ts.sentiment_label IN ('Bullish','Somewhat-Bullish') THEN 1 ELSE 0 END) AS positive,
            SUM(CASE WHEN ts.sentiment_label = 'Neutral' THEN 1 ELSE 0 END) AS neutral,
            SUM(CASE WHEN ts.sentiment_label IN ('Bearish','Somewhat-Bearish') THEN 1 ELSE 0 END) AS negative
        FROM ticker_sentiments ts
        JOIN market_news mn ON ts.article_id = mn.id
        {where}
        GROUP BY ts.ticker
        ORDER BY {sort} DESC
        LIMIT %s
    """
    params.append(limit)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


@mcp.tool()
def get_daily_summary(date: str) -> dict:
    """
    Get a summary of articles and sentiment for a specific date (YYYY-MM-DD).
    Returns article count, top sources, and top tickers by mention for that day.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT COUNT(*) AS total_articles FROM market_news WHERE DATE(published_time) = %s",
        (date,),
    )
    total = cursor.fetchone()

    cursor.execute(
        """
        SELECT source, COUNT(*) AS cnt
        FROM market_news
        WHERE DATE(published_time) = %s
        GROUP BY source ORDER BY cnt DESC LIMIT 10
        """,
        (date,),
    )
    top_sources = cursor.fetchall()

    cursor.execute(
        """
        SELECT ts.ticker, COUNT(*) AS mentions,
               ROUND(AVG(ts.sentiment_score), 4) AS avg_score
        FROM ticker_sentiments ts
        JOIN market_news mn ON ts.article_id = mn.id
        WHERE DATE(mn.published_time) = %s
        GROUP BY ts.ticker
        ORDER BY mentions DESC LIMIT 15
        """,
        (date,),
    )
    top_tickers = cursor.fetchall()

    cursor.close()
    conn.close()
    return {
        "date": date,
        "total_articles": total["total_articles"],
        "top_sources": top_sources,
        "top_tickers": top_tickers,
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
