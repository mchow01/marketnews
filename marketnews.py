#!/usr/bin/env python3
"""
Daily technology market news aggregator and WordPress poster.

Fetches technology market news and sentiment from AlphaVantage API,
then posts structured summaries to WordPress blog.
"""

from dotenv import load_dotenv
import os
import requests
import json
import base64
from datetime import datetime
import logging
import urllib3

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
        self.wordpress_url = os.getenv('WORDPRESS_URL')
        self.wordpress_user = os.getenv('WORDPRESS_USER')
        self.wordpress_password = os.getenv('WORDPRESS_PASSWORD')
        
        if not all([self.alphavantage_api_key, self.wordpress_user, self.wordpress_password]):
            raise ValueError("Missing required environment variables")
        
        # Setup WordPress API authentication
        credentials = f"{self.wordpress_user}:{self.wordpress_password}"
        token = base64.b64encode(credentials.encode()).decode('utf-8')
        self.wp_headers = {
            'Authorization': f'Basic {token}',
            'Content-Type': 'application/json'
        }
    
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
    
    def format_ticker_sentiments(self, ticker_sentiments):
        """Format ticker sentiments as unordered list."""
        if not ticker_sentiments:
            return ""
        
        sentiment_items = []
        for ticker in ticker_sentiments:
            ticker_symbol = ticker.get('ticker', 'Unknown')
            sentiment_score = float(ticker.get('ticker_sentiment_score', 0))
            sentiment_label = ticker.get('ticker_sentiment_label', 'Neutral')
            relevance = float(ticker.get('relevance_score', 0))
            
            sentiment_items.append(
                f"<li><strong>{ticker_symbol}</strong>: {sentiment_label} "
                f"(Score: {sentiment_score:.3f}, Relevance: {relevance:.3f})</li>"
            )
        
        return f"<ul>{''.join(sentiment_items)}</ul>"
    
    def create_wordpress_post(self, article):
        """Create a WordPress post from news article data."""
        title = article.get('title', 'Technology Market News')
        summary = article.get('summary', 'No summary available.')
        ticker_sentiments = article.get('ticker_sentiment', [])
        topics = [topic.get('topic', '') for topic in article.get('topics', [])]
        source = article.get('source', 'Unknown')
        url = article.get('url', '')
        published_time = article.get('time_published', '')
        
        # Format the post content
        sentiment_list = self.format_ticker_sentiments(ticker_sentiments)
        
        content = f"""
        <p><strong>Summary:</strong> {summary}</p>
        
        <h3>Ticker Sentiments:</h3>
        {sentiment_list}
        
        <p><small><strong>Source:</strong> {source}<br>
        <strong>Published:</strong> {published_time}<br>
        <strong>Original Article:</strong> <a href="{url}" target="_blank">Read more</a></small></p>
        """.strip()
        
        # Prepare post data
        post_data = {
            'title': title,
            'content': content,
            'status': 'publish'
            # Note: Tags require tag IDs, not names. Skipping for now.
        }
        
        # Post to WordPress
        wp_post_url = f"{self.wordpress_url}/wp-json/wp/v2/posts"
        
        try:
            response = requests.post(
                wp_post_url, 
                headers=self.wp_headers, 
                json=post_data,
                verify=False  # Ignore SSL certificate verification
            )
            response.raise_for_status()
            
            post_response = response.json()
            post_id = post_response.get('id')
            post_url = post_response.get('link')
            
            logger.info(f"Created WordPress post {post_id}: {title}")
            logger.info(f"Post URL: {post_url}")
            
            return post_id
        
        except requests.RequestException as e:
            logger.error(f"Error creating WordPress post: {e}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            return None
    
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
            
            post_id = self.create_wordpress_post(article)
            
            if post_id:
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