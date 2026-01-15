# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a fully Dockerized Python project for monitoring technology market news and sentiment using the AlphaVantage API. News articles are stored in a MySQL database and displayed via a Hacker News-style Flask web application. The entire system runs in Docker containers with cron-based automation for daily news fetching.

## Development Setup

This project runs in Docker containers. Docker Compose manages the MySQL database and Flask web application.

**Prerequisites:**
- Docker and Docker Compose installed
- `.env` file configured with API key

**Start the application:**
```bash
docker compose up -d
```

**Initialize database (first time only):**
```bash
docker exec marketnews-web uv run python db_setup.py
```

**Fetch news articles manually:**
```bash
docker exec marketnews-web uv run python marketnews.py
```

**View logs:**
```bash
docker logs marketnews-web
docker logs marketnews-db
```

**Stop the application:**
```bash
docker compose down
```

### Local Development (without Docker)

This project uses `uv` as the package manager. Dependencies are managed in `pyproject.toml`.

**Install dependencies:**
```bash
uv sync
```

**Run locally (requires MySQL on port 3307):**
```bash
uv run python app.py
```

## Environment Configuration

Copy `.env.example` to `.env` and configure:
- `ALPHAVANTAGE_API_KEY`: API key for AlphaVantage news and sentiment data
- Database configuration (automatically set by Docker Compose):
  - `DB_HOST`: localhost (or 'db' inside Docker)
  - `DB_PORT`: 3307 (mapped from container's 3306)
  - `DB_NAME`: marketnews
  - `DB_USER`: marketnews
  - `DB_PASSWORD`: marketnews_pass

## Core Architecture

### Docker Services
- **marketnews-db**: MySQL 8.0 database container (port 3307)
- **marketnews-web**: Flask web application with Gunicorn (port 5000)

### Python Files
- **marketnews.py**: Main program that fetches technology news and stores in MySQL database
- **app.py**: Flask web application that displays news in a Hacker News-style interface
- **db_setup.py**: Database initialization script for creating necessary tables
- **MarketNewsAggregator class**: Handles API integration, data formatting, and MySQL storage

### Docker Files
- **Dockerfile**: Builds Flask application container (Python 3.13 + uv + gunicorn)
- **docker-compose.yml**: Orchestrates MySQL and Flask services
- **.dockerignore**: Excludes unnecessary files from Docker build

## Implementation Details

- **Containerization**: Fully Dockerized with Docker Compose orchestration
- **Database**: Standalone MySQL 8.0 database (separate from WordPress, port 3307)
- **Web Server**: Gunicorn WSGI server with 4 workers for production-grade Flask serving
- **Data Storage**: Two tables - `market_news` (articles) and `ticker_sentiments` (sentiment data)
- **Data Processing**: Converts string values to floats for sentiment scores and relevance formatting
- **Error Handling**: Comprehensive logging and error recovery for API failures
- **Source Filtering**: Articles from banned sources (currently "Motley Fool") are automatically filtered out before processing
- **Web Interface**: Flask application with Hacker News-inspired minimalist design
- **Environment Variables**: All database credentials configured via environment variables

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

**Build and start Docker containers:**
```bash
docker compose build
docker compose up -d
```

**Initialize database (first time setup):**
```bash
docker exec marketnews-web uv run python db_setup.py
```

**Fetch news articles manually:**
```bash
docker exec marketnews-web uv run python marketnews.py
```

**View application logs:**
```bash
docker logs -f marketnews-web
```

**Access database:**
```bash
docker exec marketnews-db mysql -u marketnews -pmarketnews_pass marketnews
```

**Restart services:**
```bash
docker compose restart
```

**Stop and remove containers:**
```bash
docker compose down
# Or remove volumes too:
docker compose down -v
```

**Cron setup for daily execution (10:00 AM EST):**
```bash
0 10 * * * docker exec marketnews-web uv run python marketnews.py
```

## API Reference

- AlphaVantage NEWS_SENTIMENT function: https://www.alphavantage.co/documentation/
- Flask documentation: https://flask.palletsprojects.com/