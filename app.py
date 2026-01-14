#!/usr/bin/env python3
"""
Flask web application for Market News aggregator.

Displays technology market news in a Hacker News-style interface.
"""

from flask import Flask, render_template, request
import mysql.connector
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def get_db_connection():
    """Create and return MySQL database connection."""
    return mysql.connector.connect(
        host='localhost',
        port=3306,
        user='wordpress',
        password='my_wordpress_db_password',
        database='wordpress'
    )

def get_articles(limit=100, offset=0, search_query=None):
    """Fetch articles from database with optional search."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        if search_query:
            # Search by ticker symbol
            cursor.execute("""
                SELECT DISTINCT m.*
                FROM market_news m
                JOIN ticker_sentiments t ON m.id = t.article_id
                WHERE t.ticker LIKE %s
                ORDER BY m.created_at DESC
                LIMIT %s OFFSET %s
            """, (f'%{search_query}%', limit, offset))
        else:
            cursor.execute("""
                SELECT * FROM market_news
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """, (limit, offset))

        articles = cursor.fetchall()
        return articles

    finally:
        cursor.close()
        conn.close()

def get_article_by_id(article_id):
    """Fetch a single article with its ticker sentiments."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Get article
        cursor.execute("SELECT * FROM market_news WHERE id = %s", (article_id,))
        article = cursor.fetchone()

        if not article:
            return None

        # Get ticker sentiments
        cursor.execute("""
            SELECT * FROM ticker_sentiments
            WHERE article_id = %s
            ORDER BY relevance_score DESC
        """, (article_id,))
        article['tickers'] = cursor.fetchall()

        return article

    finally:
        cursor.close()
        conn.close()

def get_article_tickers(article_id):
    """Get ticker symbols for an article (for list display)."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT ticker FROM ticker_sentiments
            WHERE article_id = %s
            ORDER BY relevance_score DESC
            LIMIT 5
        """, (article_id,))
        tickers = [row['ticker'] for row in cursor.fetchall()]
        return tickers

    finally:
        cursor.close()
        conn.close()

@app.route('/')
def index():
    """Homepage with article listing."""
    search_query = request.args.get('q', '').strip()
    page = int(request.args.get('page', 1))
    per_page = 30

    offset = (page - 1) * per_page
    articles = get_articles(limit=per_page, offset=offset, search_query=search_query or None)

    # Add ticker info to each article
    for article in articles:
        article['tickers'] = get_article_tickers(article['id'])

    return render_template('index.html',
                         articles=articles,
                         page=page,
                         search_query=search_query)

@app.route('/article/<int:article_id>')
def article_detail(article_id):
    """Article detail page."""
    article = get_article_by_id(article_id)

    if not article:
        return "Article not found", 404

    return render_template('article.html', article=article)

@app.template_filter('timeago')
def timeago_filter(dt_str):
    """Convert datetime string to human-readable time ago."""
    if not dt_str:
        return 'unknown time'

    try:
        # Parse the datetime string
        if isinstance(dt_str, str):
            # Handle different datetime formats
            if 'T' in dt_str:
                # Format: 20260113T142500
                dt = datetime.strptime(dt_str[:15], '%Y%m%dT%H%M%S')
            else:
                dt = datetime.fromisoformat(str(dt_str))
        else:
            dt = dt_str

        now = datetime.now()
        diff = now - dt

        seconds = diff.total_seconds()
        minutes = seconds / 60
        hours = minutes / 60
        days = hours / 24

        if days >= 1:
            return f"{int(days)} day{'s' if days >= 2 else ''} ago"
        elif hours >= 1:
            return f"{int(hours)} hour{'s' if hours >= 2 else ''} ago"
        elif minutes >= 1:
            return f"{int(minutes)} minute{'s' if minutes >= 2 else ''} ago"
        else:
            return "just now"

    except Exception as e:
        logger.error(f"Error parsing datetime: {e}")
        return str(dt_str)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
