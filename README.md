# Technology Market News Aggregator

Daily monitor of technology market news and sentiment that automatically posts to WordPress.

## Overview

This project fetches technology market news from the AlphaVantage API and automatically posts structured summaries to a WordPress blog. Each news article is formatted with summaries, ticker sentiment analysis, and source information.

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
   - `WORDPRESS_URL`: Your WordPress site URL
   - `WORDPRESS_USER`: WordPress username
   - `WORDPRESS_PASSWORD`: WordPress Application Password

3. **Generate WordPress Application Password:**
   - Go to WordPress Admin → Users → Profile
   - Scroll to "Application Passwords" section
   - Enter application name and click "Add New Application Password"
   - Copy the generated password to your `.env` file

## Usage

**Run manually:**
```bash
uv run python marketnews.py
```

**Test AlphaVantage API:**
```bash
uv run python sample.py
```

**Schedule with cron (daily at noon):**
```bash
crontab -e
# Add: 0 12 * * * cd /path/to/marketnews && uv run python marketnews.py
```

If the above doesn't work, then...

```bash
crontab -e
# Add: * 12 * * * cd /path/to/marketnews && /path/to/marketnews/.venv/bin/python marketnews.py
```

## Features

- Fetches up to 50 technology news articles from AlphaVantage API
- **Source filtering**: Automatically excludes articles from banned sources (currently "Motley Fool")
- Creates WordPress posts with structured content:
  - Article title
  - Summary
  - Ticker sentiment analysis (with scores and relevance)
  - Source and publication information
  - Link to original article
- Handles self-signed SSL certificates
- Comprehensive logging for monitoring
- Error handling and retry logic

## Files

- **`marketnews.py`**: Main program for automated news aggregation
- **`sample.py`**: Test script for AlphaVantage API integration
- **`.env.example`**: Template for environment configuration
- **`pyproject.toml`**: Python dependencies managed by uv

## References

- [AlphaVantage API Documentation](https://www.alphavantage.co/documentation/)
- [WordPress REST API Documentation](https://developer.wordpress.org/rest-api/)