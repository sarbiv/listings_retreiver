"""
Scrapy settings for luxury development scraper
"""
import os
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent

# Scrapy settings
BOT_NAME = 'luxury_scraper'
SPIDER_MODULES = ['scraper.spiders']
NEWSPIDER_MODULE = 'scraper.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 2

# Configure a delay for requests for the same website (default: 0)
DOWNLOAD_DELAY = 3.0
RANDOMIZE_DOWNLOAD_DELAY = 0.5

# Enable autothrottling
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
AUTOTHROTTLE_DEBUG = False

# Configure pipelines
ITEM_PIPELINES = {
    'scraper.pipelines.clean_normalize.CleanNormalizePipeline': 100,
    'scraper.pipelines.dedupe.DedupePipeline': 200,
    'scraper.pipelines.database.DatabasePipeline': 300,
}

# Configure middlewares
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scraper.middlewares.RotateUserAgentMiddleware': 400,
}

# User agent
USER_AGENT = 'LuxuryScraper/1.0 (+https://example.com/bot)'

# Disable cookies
COOKIES_ENABLED = False

# Disable Telnet Console
TELNETCONSOLE_ENABLED = False

# Configure logging
LOG_LEVEL = 'INFO'
LOG_FILE = PROJECT_ROOT / 'data' / 'scraper.log'

# Database settings
DATABASE_URL = f"sqlite:///{PROJECT_ROOT / 'data' / 'luxury_developments.db'}"

# Data directories
DATA_DIR = PROJECT_ROOT / 'data'
EXPORTS_DIR = DATA_DIR / 'exports'
CACHE_DIR = DATA_DIR / 'cache'

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
EXPORTS_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)
