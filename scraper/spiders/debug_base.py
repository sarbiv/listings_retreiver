"""
Debug base spider with HTML capture
"""
import structlog
from typing import Dict, Any, List
from scrapy.http import Response
from scrapy import Spider
from ..utils.html import text_or_none, clean_text

logger = structlog.get_logger()

class DebugBaseSpider(Spider):
    """Base spider with debug capabilities"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.debug_data = {
            'pages_processed': 0,
            'raw_html_samples': [],
            'parsed_data': [],
            'errors': []
        }
    
    def parse(self, response: Response):
        """Parse response with debug information"""
        try:
            self.debug_data['pages_processed'] += 1
            
            # Capture raw HTML sample
            html_sample = {
                'url': response.url,
                'status': response.status,
                'title': response.css('title::text').get(),
                'html_length': len(response.text),
                'html': response.text[:2000],  # First 2000 chars
                'key_elements': self.extract_key_elements(response)
            }
            self.debug_data['raw_html_samples'].append(html_sample)
            
            logger.info("DEBUG: Page processed", 
                       url=response.url,
                       status=response.status,
                       title=html_sample['title'],
                       html_length=html_sample['html_length'])
            
            # Extract data using spider-specific methods
            item = self.extract_debug_data(response)
            
            if item:
                self.debug_data['parsed_data'].append(item)
                yield item
            
        except Exception as e:
            error_msg = f"Parse error: {str(e)}"
            logger.error("DEBUG: Parse error", error=error_msg, url=response.url)
            self.debug_data['errors'].append({
                'url': response.url,
                'error': error_msg
            })
    
    def extract_key_elements(self, response: Response) -> List[str]:
        """Extract key elements from HTML for debugging"""
        elements = []
        
        # Check for common project elements
        if response.css('h1::text').get():
            elements.append(f"H1: {response.css('h1::text').get()[:50]}")
        
        if response.css('.project-title::text').get():
            elements.append(f"Project Title: {response.css('.project-title::text').get()[:50]}")
        
        if response.css('.developer::text').get():
            elements.append(f"Developer: {response.css('.developer::text').get()[:50]}")
        
        if response.css('.price::text').get():
            elements.append(f"Price: {response.css('.price::text').get()[:50]}")
        
        if response.css('.amenities').get():
            elements.append("Amenities section found")
        
        if response.css('.gallery').get():
            elements.append("Gallery section found")
        
        if response.css('a[href*="virtual"]').get():
            elements.append("Virtual tour links found")
        
        if response.css('a[href*="brochure"]').get():
            elements.append("Brochure links found")
        
        # Check for listing containers (for discovery spiders)
        listing_selectors = [
            '.listing', '.property', '.project', '.development',
            '.card', '.item', '.result', '.search-result'
        ]
        
        for selector in listing_selectors:
            if response.css(selector).get():
                elements.append(f"Listing container found: {selector}")
        
        return elements
    
    def extract_debug_data(self, response: Response) -> Dict[str, Any]:
        """Extract data for debugging - to be overridden by specific spiders"""
        return {
            'project': {
                'name': text_or_none(response, 'h1::text, .project-title::text'),
                'url': response.url
            },
            'source': {
                'source_name': self.name,
                'source_url': response.url
            }
        }
    
    def closed(self, reason):
        """Called when spider closes"""
        logger.info("DEBUG: Spider closed", 
                   spider=self.name,
                   reason=reason,
                   pages_processed=self.debug_data['pages_processed'])
        
        # Print debug summary
        print(f"\n🔍 DEBUG SUMMARY: {self.name}")
        print("=" * 60)
        print(f"Pages processed: {self.debug_data['pages_processed']}")
        print(f"Raw HTML samples: {len(self.debug_data['raw_html_samples'])}")
        print(f"Parsed data items: {len(self.debug_data['parsed_data'])}")
        print(f"Errors: {len(self.debug_data['errors'])}")
        
        if self.debug_data['errors']:
            print("\nErrors encountered:")
            for error in self.debug_data['errors']:
                print(f"  - {error['error']} (URL: {error['url']})")
        
        # Save debug data
        import json
        debug_file = f"debug_{self.name}.json"
        with open(debug_file, 'w') as f:
            json.dump(self.debug_data, f, indent=2, default=str)
        print(f"Debug data saved to: {debug_file}")
