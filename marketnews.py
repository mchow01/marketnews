#!/usr/bin/env python3
"""
Daily technology market news aggregator.

Fetches technology market news and sentiment from AlphaVantage API,
then stores articles and ticker sentiments in MySQL database.
"""

from dotenv import load_dotenv
import os
import requests
import json
from datetime import datetime
import logging
import mysql.connector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MarketNewsAggregator:
    def __init__(self):
        load_dotenv()
        self.alphavantage_api_key = os.getenv('ALPHAVANTAGE_API_KEY')

        if not self.alphavantage_api_key:
            raise ValueError("Missing ALPHAVANTAGE_API_KEY environment variable")

    def get_db_connection(self):
        """Create and return MySQL database connection."""
        return mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 3307)),
            user=os.getenv('DB_USER', 'marketnews'),
            password=os.getenv('DB_PASSWORD', 'marketnews_pass'),
            database=os.getenv('DB_NAME', 'marketnews')
        )
    
    def fetch_technology_news(self):
        """Fetch technology market news from AlphaVantage API."""
        url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&topics=technology&apikey={self.alphavantage_api_key}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            if 'feed' not in data:
                logger.error("No feed data in API response")
                return []
            
            logger.info(f"Fetched {len(data['feed'])} news articles")
            return data['feed']
        
        except requests.RequestException as e:
            logger.error(f"Error fetching news: {e}")
            return []
    
    def insert_article(self, article):
        """Insert article into market_news table and return article ID."""
        title = article.get('title', 'Technology Market News')
        summary = article.get('summary', 'No summary available.')
        url = article.get('url', '')
        source = article.get('source', 'Unknown')
        published_time = article.get('time_published', '')

        conn = self.get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO market_news (title, summary, url, source, published_time)
                VALUES (%s, %s, %s, %s, %s)
            """, (title, summary, url, source, published_time))

            conn.commit()
            article_id = cursor.lastrowid

            logger.info(f"Inserted article {article_id}: {title[:50]}...")
            return article_id

        except mysql.connector.Error as e:
            logger.error(f"Error inserting article: {e}")
            conn.rollback()
            return None

        finally:
            cursor.close()
            conn.close()

    def insert_ticker_sentiments(self, article_id, ticker_sentiments):
        """Insert ticker sentiments for an article."""
        if not ticker_sentiments:
            return

        conn = self.get_db_connection()
        cursor = conn.cursor()

        try:
            for ticker in ticker_sentiments:
                ticker_symbol = ticker.get('ticker', 'Unknown')
                sentiment_label = ticker.get('ticker_sentiment_label', 'Neutral')
                sentiment_score = float(ticker.get('ticker_sentiment_score', 0))
                relevance_score = float(ticker.get('relevance_score', 0))

                cursor.execute("""
                    INSERT INTO ticker_sentiments
                    (article_id, ticker, sentiment_label, sentiment_score, relevance_score)
                    VALUES (%s, %s, %s, %s, %s)
                """, (article_id, ticker_symbol, sentiment_label, sentiment_score, relevance_score))

            conn.commit()
            logger.info(f"Inserted {len(ticker_sentiments)} ticker sentiments for article {article_id}")

        except mysql.connector.Error as e:
            logger.error(f"Error inserting ticker sentiments: {e}")
            conn.rollback()

        finally:
            cursor.close()
            conn.close()
    
    def run(self):
        """Main execution function."""
        logger.info("Starting technology market news aggregation")
        
        # Fetch news from AlphaVantage
        articles = self.fetch_technology_news()
        
        if not articles:
            logger.warning("No articles to process")
            return
        
        # Filter out banned sources
        filtered_articles = []
        banned_sources = ['Motley Fool']
        
        for article in articles:
            source = article.get('source', '')
            if source not in banned_sources:
                filtered_articles.append(article)
            else:
                logger.info(f"Filtered out article from banned source: {source}")
        
        logger.info(f"Filtered {len(articles) - len(filtered_articles)} articles from banned sources")
        
        # Process each filtered article
        successful_posts = 0
        failed_posts = 0

        for i, article in enumerate(filtered_articles, 1):
            logger.info(f"Processing article {i}/{len(filtered_articles)}: {article.get('title', 'Unknown')[:50]}...")

            # Insert article into database
            article_id = self.insert_article(article)

            if article_id:
                # Insert ticker sentiments
                ticker_sentiments = article.get('ticker_sentiment', [])
                self.insert_ticker_sentiments(article_id, ticker_sentiments)
                successful_posts += 1
            else:
                failed_posts += 1

        logger.info(f"Completed processing: {successful_posts} successful, {failed_posts} failed")

def main():
    """Entry point for cron execution."""
    try:
        aggregator = MarketNewsAggregator()
        aggregator.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise

if __name__ == "__main__":
    main()