# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python project for monitoring technology market news and sentiment using the AlphaVantage API. News articles are stored in a MySQL database and displayed via a Hacker News-style Flask web application. The system runs via cron to fetch news daily.

## Development Setup

This project uses `uv` as the package manager. Dependencies are managed in `pyproject.toml`.

**Install dependencies:**
```bash
uv sync
```

**Run the sample script:**
```bash
uv run python sample.py
```

**Run the main program (fetch and store news):**
```bash
uv run python marketnews.py
```

**Run the Flask web application:**
```bash
uv run python app.py
```

**Initialize database tables:**
```bash
uv run python db_setup.py
```

## Environment Configuration

Copy `.env.example` to `.env` and configure:
- `ALPHAVANTAGE_API_KEY`: API key for AlphaVantage news and sentiment data
- Database credentials are hardcoded to match the docker-compose WordPress MySQL setup (localhost:3306, user: wordpress)

## Core Architecture

- **sample.py**: Working example that demonstrates AlphaVantage API integration for technology news sentiment
- **marketnews.py**: Main program that fetches technology news and stores in MySQL database
- **app.py**: Flask web application that displays news in a Hacker News-style interface
- **db_setup.py**: Database initialization script for creating necessary tables
- **MarketNewsAggregator class**: Handles API integration, data formatting, and MySQL storage

## Implementation Details

- **Database**: MySQL database shared with WordPress docker container (localhost:3306)
- **Data Storage**: Two tables - `market_news` (articles) and `ticker_sentiments` (sentiment data)
- **Data Processing**: Converts string values to floats for sentiment scores and relevance formatting
- **Error Handling**: Comprehensive logging and error recovery for API failures
- **Source Filtering**: Articles from banned sources (currently "Motley Fool") are automatically filtered out before processing
- **Web Interface**: Flask application with Hacker News-inspired minimalist design

## Database Schema

### market_news table
- `id`: Auto-increment primary key
- `title`: Article title (VARCHAR 500)
- `summary`: Article summary (TEXT)
- `url`: Original article URL (VARCHAR 1000)
- `source`: News source (VARCHAR 200)
- `published_time`: Publication timestamp from AlphaVantage
- `created_at`: Insertion timestamp

### ticker_sentiments table
- `id`: Auto-increment primary key
- `article_id`: Foreign key to market_news
- `ticker`: Stock ticker symbol (VARCHAR 20)
- `sentiment_label`: Sentiment label (e.g., "Bullish", "Neutral")
- `sentiment_score`: Numerical sentiment score (DECIMAL)
- `relevance_score`: Relevance score (DECIMAL)

## Web Application Features

- **Homepage**: Lists articles in Hacker News style with numbered entries
- **Search**: Search by ticker symbol
- **Article Details**: Full article view with summary and ticker sentiment table
- **Pagination**: 30 articles per page with "More" navigation
- **Time Display**: Human-readable "time ago" format (e.g., "2 hours ago")

## Development Commands

**Initialize database (first time setup):**
```bash
uv run python db_setup.py
```

**Test AlphaVantage API response:**
```bash
uv run python sample.py
```

**Run news aggregation (fetch and store articles):**
```bash
uv run python marketnews.py
```

**Start Flask web application:**
```bash
uv run python app.py
# Access at http://localhost:5000 or http://192.168.1.18:5000
```

**Cron setup for daily execution (currently 10:00 AM):**
```bash
0 10 * * * cd /home/defcon/repos/marketnews && /home/defcon/repos/marketnews/.venv/bin/python marketnews.py
```

## API Reference

- AlphaVantage NEWS_SENTIMENT function: https://www.alphavantage.co/documentation/
- Flask documentation: https://flask.palletsprojects.com/