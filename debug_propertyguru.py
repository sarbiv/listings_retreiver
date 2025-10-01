#!/usr/bin/env python3
"""
Debug PropertyGuru spider to see why it's not finding listings
"""
import sys
from pathlib import Path
import structlog

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
        structlog.dev.ConsoleRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

class DebugPropertyGuruSpider:
    """Debug version of PropertyGuru spider"""
    
    name = 'debug_propertyguru_sg'
    allowed_domains = ['propertyguru.com.sg']
    start_urls = ['https://www.propertyguru.com.sg/new-project-launch']
    
    def parse(self, response):
        """Parse with detailed debugging"""
        print(f"\n🔍 DEBUG: Parsing {response.url}")
        print(f"Status: {response.status}")
        print(f"HTML Length: {len(response.text)}")
        
        # Check title
        title = response.css('title::text').get()
        print(f"Page Title: {title}")
        
        # Look for listing containers
        listing_selectors = [
            '.listing-card',
            '.property-card', 
            '.project-card',
            '.search-result',
            '.listing',
            '.property',
            '.project'
        ]
        
        print(f"\n🔍 Looking for listing containers:")
        for selector in listing_selectors:
            elements = response.css(selector)
            count = len(elements)
            print(f"  {selector}: {count} elements")
            
            if count > 0:
                # Show first element
                first_element = elements[0]
                print(f"    First element text: {first_element.get()[:200]}...")
        
        # Look for project links
        project_links = response.css('a[href*="/new-project/"]::attr(href)').getall()
        print(f"\n🔍 Project links found: {len(project_links)}")
        for i, link in enumerate(project_links[:5]):
            print(f"  {i+1}: {link}")
        
        # Look for any links with "project" in them
        all_links = response.css('a::attr(href)').getall()
        project_related_links = [link for link in all_links if 'project' in link.lower()]
        print(f"\n🔍 All project-related links: {len(project_related_links)}")
        for i, link in enumerate(project_related_links[:10]):
            print(f"  {i+1}: {link}")
        
        # Check for JavaScript-rendered content
        if 'loading' in response.text.lower() or 'javascript' in response.text.lower():
            print(f"\n⚠️  Page may require JavaScript rendering")
        
        # Save HTML sample
        with open('debug_propertyguru.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"\n💾 HTML saved to: debug_propertyguru.html")

def main():
    """Run debug spider"""
    print("🔍 DEBUG: PropertyGuru Singapore Spider")
    print("=" * 50)
    
    settings = get_project_settings()
    settings.set('LOG_LEVEL', 'DEBUG')
    settings.set('CLOSESPIDER_PAGECOUNT', 1)
    
    # Enable Playwright for JavaScript rendering
    settings.set('DOWNLOAD_HANDLERS', {
        "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    })
    settings.set('TWISTED_REACTOR', 'twisted.internet.asyncioreactor.AsyncioSelectorReactor')
    settings.set('PLAYWRIGHT_BROWSER_TYPE', 'chromium')
    settings.set('PLAYWRIGHT_LAUNCH_OPTIONS', {'headless': True})
    
    process = CrawlerProcess(settings)
    process.crawl(DebugPropertyGuruSpider)
    process.start()

if __name__ == '__main__':
    main()
