#!/usr/bin/env python3
"""
Debug mode for spider parsing - shows raw HTML, parsed data, and database writes
"""
import sys
import os
from pathlib import Path
import json
import structlog
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure detailed logging
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

class DebugSpider:
    """Debug wrapper for spiders"""
    
    def __init__(self, spider_name):
        self.spider_name = spider_name
        self.debug_data = {
            'spider_name': spider_name,
            'pages_processed': 0,
            'raw_html_samples': [],
            'parsed_data': [],
            'database_writes': [],
            'errors': []
        }
    
    def run_debug(self, max_pages=2):
        """Run spider in debug mode"""
        print(f"🔍 DEBUG MODE: {self.spider_name}")
        print("=" * 60)
        
        # Get spider class
        spider_class = self.get_spider_class()
        if not spider_class:
            print(f"❌ Spider {self.spider_name} not found")
            return
        
        # Create custom settings for debug mode
        settings = get_project_settings()
        settings.set('LOG_LEVEL', 'DEBUG')
        settings.set('CLOSESPIDER_PAGECOUNT', max_pages)
        
        # Enable Playwright for JavaScript rendering
        settings.set('DOWNLOAD_HANDLERS', {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        })
        settings.set('TWISTED_REACTOR', 'twisted.internet.asyncioreactor.AsyncioSelectorReactor')
        settings.set('PLAYWRIGHT_BROWSER_TYPE', 'chromium')
        settings.set('PLAYWRIGHT_LAUNCH_OPTIONS', {'headless': True})
        
        # Add custom pipeline for debugging
        settings.set('ITEM_PIPELINES', {
            'scraper.pipelines.debug.DebugPipeline': 100,
            'scraper.pipelines.clean_normalize.CleanNormalizePipeline': 200,
            'scraper.pipelines.dedupe.DedupePipeline': 300,
            'scraper.pipelines.database.DatabasePipeline': 400,
        })
        
        # Run spider
        process = CrawlerProcess(settings)
        process.crawl(spider_class, debug_callback=self.debug_callback)
        process.start()
        
        # Print debug summary
        self.print_debug_summary()
    
    def get_spider_class(self):
        """Get spider class by name"""
        spider_mapping = {
            'selene_fort_lauderdale': 'scraper.spiders.tier_a.selene_fort_lauderdale.SeleneFortLauderdaleSpider',
            'pier_sixty_six': 'scraper.spiders.tier_a.pier_sixty_six.PierSixtySixSpider',
            'berkeley_oval_village': 'scraper.spiders.tier_a.berkeley_oval_village.BerkeleyOvalVillageSpider',
            'propertyguru_sg': 'scraper.spiders.tier_b.propertyguru_sg.PropertyGuruSGSpider',
            'opr_dubai': 'scraper.spiders.tier_b.opr_dubai.OPRDubaiSpider',
            'corcoran_sunshine_nyc': 'scraper.spiders.tier_b.corcoran_sunshine_nyc.CorcoranSunshineNYCSpider',
        }
        
        if self.spider_name not in spider_mapping:
            return None
        
        module_path, class_name = spider_mapping[self.spider_name].rsplit('.', 1)
        module = __import__(module_path, fromlist=[class_name])
        return getattr(module, class_name)
    
    def debug_callback(self, debug_data):
        """Callback to receive debug data from spider"""
        self.debug_data.update(debug_data)
    
    def print_debug_summary(self):
        """Print comprehensive debug summary"""
        print(f"\n🔍 DEBUG SUMMARY: {self.spider_name}")
        print("=" * 60)
        
        print(f"📊 Pages Processed: {self.debug_data.get('pages_processed', 0)}")
        print(f"📝 Raw HTML Samples: {len(self.debug_data.get('raw_html_samples', []))}")
        print(f"🔧 Parsed Data Items: {len(self.debug_data.get('parsed_data', []))}")
        print(f"💾 Database Writes: {len(self.debug_data.get('database_writes', []))}")
        print(f"❌ Errors: {len(self.debug_data.get('errors', []))}")
        
        # Show raw HTML samples
        if self.debug_data.get('raw_html_samples'):
            print(f"\n📄 RAW HTML SAMPLES:")
            print("-" * 40)
            for i, sample in enumerate(self.debug_data['raw_html_samples'][:3]):
                print(f"Sample {i+1} (URL: {sample.get('url', 'Unknown')}):")
                print(f"  Length: {len(sample.get('html', ''))} characters")
                print(f"  Title: {sample.get('title', 'No title')}")
                print(f"  Key Elements Found:")
                for element in sample.get('key_elements', []):
                    print(f"    - {element}")
                print()
        
        # Show parsed data
        if self.debug_data.get('parsed_data'):
            print(f"\n🔧 PARSED DATA:")
            print("-" * 40)
            for i, item in enumerate(self.debug_data['parsed_data'][:2]):
                print(f"Item {i+1}:")
                print(f"  Project: {item.get('project', {}).get('name', 'No name')}")
                print(f"  Units: {len(item.get('units', []))}")
                print(f"  Amenities: {len(item.get('amenities', []))}")
                print(f"  Media Links: {len(item.get('media_links', []))}")
                print(f"  Source: {item.get('source', {}).get('source_name', 'No source')}")
                print()
        
        # Show database writes
        if self.debug_data.get('database_writes'):
            print(f"\n💾 DATABASE WRITES:")
            print("-" * 40)
            for i, write in enumerate(self.debug_data['database_writes'][:3]):
                print(f"Write {i+1}:")
                print(f"  Table: {write.get('table', 'Unknown')}")
                print(f"  Action: {write.get('action', 'Unknown')}")
                print(f"  Data: {json.dumps(write.get('data', {}), indent=2)[:200]}...")
                print()
        
        # Show errors
        if self.debug_data.get('errors'):
            print(f"\n❌ ERRORS:")
            print("-" * 40)
            for i, error in enumerate(self.debug_data['errors']):
                print(f"Error {i+1}: {error}")
                print()
        
        # Save debug data to file
        debug_file = f"debug_{self.spider_name}.json"
        with open(debug_file, 'w') as f:
            json.dump(self.debug_data, f, indent=2, default=str)
        print(f"💾 Debug data saved to: {debug_file}")

def main():
    """Main debug function"""
    if len(sys.argv) < 2:
        print("Usage: python debug_spider.py <spider_name> [max_pages]")
        print("Available spiders:")
        print("  - selene_fort_lauderdale")
        print("  - pier_sixty_six")
        print("  - berkeley_oval_village")
        print("  - propertyguru_sg")
        print("  - opr_dubai")
        print("  - corcoran_sunshine_nyc")
        return
    
    spider_name = sys.argv[1]
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    
    debug_spider = DebugSpider(spider_name)
    debug_spider.run_debug(max_pages)

if __name__ == '__main__':
    main()
