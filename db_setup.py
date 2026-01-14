#!/usr/bin/env python3
"""
Database setup script for Market News aggregator.

Creates necessary tables in MySQL database for storing news articles
and ticker sentiments.
"""

import mysql.connector
from dotenv import load_dotenv
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Create and return MySQL database connection."""
    load_dotenv()

    # Get credentials from environment variables
    connection = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 3307)),
        user=os.getenv('DB_USER', 'marketnews'),
        password=os.getenv('DB_PASSWORD', 'marketnews_pass'),
        database=os.getenv('DB_NAME', 'marketnews')
    )

    return connection

def create_tables():
    """Create market_news and ticker_sentiments tables."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Create market_news table
        logger.info("Creating market_news table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_news (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                summary TEXT,
                url VARCHAR(1000),
                source VARCHAR(200),
                published_time VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_created_at (created_at),
                INDEX idx_source (source)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        logger.info("market_news table created successfully")

        # Create ticker_sentiments table
        logger.info("Creating ticker_sentiments table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ticker_sentiments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                article_id INT NOT NULL,
                ticker VARCHAR(20) NOT NULL,
                sentiment_label VARCHAR(50),
                sentiment_score DECIMAL(10, 6),
                relevance_score DECIMAL(10, 6),
                FOREIGN KEY (article_id) REFERENCES market_news(id) ON DELETE CASCADE,
                INDEX idx_ticker (ticker),
                INDEX idx_article_id (article_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        logger.info("ticker_sentiments table created successfully")

        conn.commit()
        logger.info("All tables created successfully!")

    except mysql.connector.Error as e:
        logger.error(f"Database error: {e}")
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

def verify_tables():
    """Verify that tables were created successfully."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SHOW TABLES LIKE 'market_%'")
        tables = cursor.fetchall()

        logger.info(f"Found {len(tables)} tables:")
        for table in tables:
            logger.info(f"  - {table[0]}")

    finally:
        cursor.close()
        conn.close()

def main():
    """Main execution function."""
    logger.info("Starting database setup...")

    try:
        create_tables()
        verify_tables()
        logger.info("Database setup completed successfully!")

    except Exception as e:
        logger.error(f"Setup failed: {e}")
        raise

if __name__ == "__main__":
    main()
