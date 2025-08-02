# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python project for monitoring technology market news and sentiment using the AlphaVantage API and posting results to a WordPress blog. The goal is to create an automated daily news aggregation system that runs via cron.

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

**Run the main program:**
```bash
uv run python marketnews.py
```

## Environment Configuration

Copy `.env.example` to `.env` and configure:
- `ALPHAVANTAGE_API_KEY`: API key for AlphaVantage news and sentiment data
- `WORDPRESS_URL`: WordPress blog URL (default: https://192.168.1.18)
- `WORDPRESS_USER`: WordPress username
- `WORDPRESS_PASSWORD`: WordPress Application Password (generate in WP Admin → Users → Profile → Application Passwords)

## Core Architecture

- **sample.py**: Working example that demonstrates AlphaVantage API integration for technology news sentiment
- **marketnews.py**: Main program that fetches technology news and posts to WordPress blog
- **MarketNewsAggregator class**: Handles API integration, data formatting, and WordPress posting

## Implementation Details

- **SSL Handling**: Script bypasses SSL verification for self-signed certificates using `verify=False`
- **Data Processing**: Converts string values to floats for sentiment scores and relevance formatting
- **Error Handling**: Comprehensive logging and error recovery for API failures
- **WordPress Integration**: Uses REST API with Basic Authentication (Application Passwords)
- **Source Filtering**: Articles from banned sources (currently "Motley Fool") are automatically filtered out before processing

## WordPress Post Structure

Each news article is formatted as:
- **Title**: Article title from AlphaVantage
- **Body**: Article summary + HTML unordered list of ticker sentiments with scores and relevance
- **Content includes**: Source, publication time, link to original article
- **Tags**: Currently disabled (WordPress API requires tag IDs, not names)

## Development Commands

**Test AlphaVantage API response:**
```bash
uv run python sample.py
```

**Run full news aggregation:**
```bash
uv run python marketnews.py
```

**Cron setup for daily execution:**
```bash
0 12 * * * cd /path/to/marketnews && uv run python marketnews.py
```

## API Reference

- AlphaVantage NEWS_SENTIMENT function: https://www.alphavantage.co/documentation/
- WordPress REST API Posts: https://developer.wordpress.org/rest-api/reference/posts/