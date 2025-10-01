#!/usr/bin/env python3
"""
Simple script to run the luxury development scraper
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

def run_spider(spider_name: str, max_pages: int = 5):
    """Run a specific spider"""
    # Set the project settings
    os.environ['SCRAPY_SETTINGS_MODULE'] = 'scraper.settings'
    
    # Get settings
    settings = get_project_settings()
    
    # Override settings for testing
    settings.set('CLOSESPIDER_PAGECOUNT', max_pages)
    settings.set('LOG_LEVEL', 'INFO')
    
    # Create crawler process
    process = CrawlerProcess(settings)
    
    # Add the spider
    process.crawl(spider_name)
    
    # Start crawling
    process.start()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python run_spider.py <spider_name> [max_pages]")
        print("Available spiders:")
        print("  - selene_fort_lauderdale")
        print("  - pier_sixty_six")
        print("  - berkeley_oval_village")
        print("  - propertyguru_sg")
        print("  - opr_dubai")
        print("  - corcoran_sunshine_nyc")
        sys.exit(1)
    
    spider_name = sys.argv[1]
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    print(f"Running spider: {spider_name} (max pages: {max_pages})")
    run_spider(spider_name, max_pages)
