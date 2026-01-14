# Technology Market News Aggregator

Daily monitor of technology market news and sentiment displayed in a Hacker News-style web interface.

## Overview

This project fetches technology market news from the AlphaVantage API, stores articles in a MySQL database, and displays them via a Flask web application with a minimalist Hacker News-inspired design. Each news article includes summaries, ticker sentiment analysis, and source information.

## Setup

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   ```

   Then edit `.env` with your credentials:
   - `ALPHAVANTAGE_API_KEY`: Your AlphaVantage API key
   - Database credentials are already configured for the local MySQL setup

3. **Initialize database:**
   ```bash
   uv run python db_setup.py
   ```

   This creates two tables in the MySQL database:
   - `market_news`: Stores article information
   - `ticker_sentiments`: Stores ticker sentiment data

## Usage

**Fetch news articles (run manually):**
```bash
uv run python marketnews.py
```

**Start the Flask web application:**
```bash
uv run python app.py
```

Then visit:
- `http://localhost:5000` (local access)
- `http://192.168.1.18:5000` (network access)

**Test AlphaVantage API:**
```bash
uv run python sample.py
```

**Automated daily execution:**
The cron job runs daily at 10:00 AM EST:
```bash
0 10 * * * cd /home/defcon/repos/marketnews && /home/defcon/repos/marketnews/.venv/bin/python marketnews.py
```

## Features

- **News Aggregation**: Fetches up to 50 technology news articles from AlphaVantage API daily
- **Source Filtering**: Automatically excludes articles from banned sources (currently "Motley Fool")
- **MySQL Storage**: Stores articles and ticker sentiments in structured database tables
- **Hacker News-Style UI**: Clean, minimalist web interface inspired by Hacker News
  - Orange header bar (#ff6600)
  - Numbered article list
  - Time ago display (e.g., "2 hours ago")
  - Clickable ticker symbols
- **Search Functionality**: Search articles by ticker symbol
- **Article Details**: Full article view with:
  - Complete summary
  - Ticker sentiment table with scores and relevance
  - Link to original article
- **Pagination**: 30 articles per page with "More" navigation
- **Comprehensive Logging**: Full logging for monitoring and debugging
- **Error Handling**: Robust error recovery for API failures

## Files

- **`marketnews.py`**: Main program for fetching news and storing in MySQL
- **`app.py`**: Flask web application with Hacker News-style interface
- **`db_setup.py`**: Database initialization script
- **`sample.py`**: Test script for AlphaVantage API integration
- **`templates/`**: Flask HTML templates (layout, index, article detail)
- **`static/`**: CSS stylesheets (Hacker News-inspired design)
- **`.env.example`**: Template for environment configuration
- **`pyproject.toml`**: Python dependencies managed by uv

## Database Schema

**market_news table:**
- `id`, `title`, `summary`, `url`, `source`, `published_time`, `created_at`

**ticker_sentiments table:**
- `id`, `article_id`, `ticker`, `sentiment_label`, `sentiment_score`, `relevance_score`

## References

- [AlphaVantage API Documentation](https://www.alphavantage.co/documentation/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Hacker News](https://news.ycombinator.com/)