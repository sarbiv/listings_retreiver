"""
Spider for Selene Oceanfront Residences (Fort Lauderdale)
"""
import scrapy
import structlog
from typing import Dict, Any, List
from scrapy.http import Response
from .base_spider import BaseTierASpider
from ..utils.html import text_or_none, clean_text

logger = structlog.get_logger()

class SeleneFortLauderdaleSpider(BaseTierASpider):
    """Spider for Selene Oceanfront Residences"""
    
    name = 'selene_fort_lauderdale'
    allowed_domains = ['selenefortlauderdale.com']
    start_urls = ['https://selenefortlauderdale.com/']
    
    def extract_spider_specific_project_data(self, response: Response) -> Dict[str, Any]:
        """Extract Selene-specific project data"""
        selector = response.selector
        
        project_data = {}
        
        # Extract project name
        name = text_or_none(selector, 'h1::text, .hero-title::text, .project-title::text')
        if name:
            project_data['name'] = name
        
        # Extract developer
        developer = text_or_none(selector, '.developer::text, .builder::text, .company::text')
        if developer:
            project_data['developer_name'] = developer
        
        # Extract description
        description = text_or_none(selector, '.description::text, .overview::text, .summary::text')
        if description:
            project_data['description'] = description
        
        # Extract address/location
        address = text_or_none(selector, '.address::text, .location::text, .project-address::text')
        if address:
            project_data['address'] = address
        
        # Set location details
        project_data['city'] = 'Fort Lauderdale'
        project_data['country'] = 'United States'
        project_data['property_type'] = 'Residential'
        
        # Extract status
        status = text_or_none(selector, '.status::text, .phase::text, .construction-status::text')
        if status:
            project_data['status'] = status.lower()
        
        # Extract completion date
        completion = text_or_none(selector, '.completion::text, .completion-date::text, .delivery::text')
        if completion:
            project_data['est_completion'] = completion
        
        # Extract price information
        price = text_or_none(selector, '.price::text, .starting-price::text, .cost::text')
        if price:
            project_data['price_info'] = price
        
        return project_data
    
    def extract_spider_specific_amenities(self, response: Response) -> List[str]:
        """Extract Selene-specific amenities with deduplication"""
        selector = response.selector
        amenities = []
        seen_amenities = set()
        
        # Look for specific amenity sections
        amenity_sections = selector.css('.amenities, .features, .facilities, .amenity-list')
        
        for section in amenity_sections:
            amenity_items = section.css('li::text, .amenity::text, .feature::text').getall()
            for item in amenity_items:
                if item and len(item.strip()) > 2:
                    cleaned_item = clean_text(item)
                    if cleaned_item and cleaned_item not in seen_amenities and self.is_valid_amenity(cleaned_item):
                        amenities.append(cleaned_item)
                        seen_amenities.add(cleaned_item)
        
        # Look for specific luxury amenities
        luxury_amenities = [
            'Oceanfront Location',
            'Private Beach Access',
            'Resort-Style Pool',
            'Fitness Center',
            'Concierge Service',
            'Valet Parking',
            'Rooftop Deck',
            'Spa Services'
        ]
        
        page_text = selector.get().lower()
        for amenity in luxury_amenities:
            if amenity.lower() in page_text and amenity not in seen_amenities:
                amenities.append(amenity)
                seen_amenities.add(amenity)
        
        return amenities
    
    def is_valid_amenity(self, amenity: str) -> bool:
        """Check if amenity is valid"""
        if not amenity or not isinstance(amenity, str):
            return False
        
        # Remove whitespace
        amenity = amenity.strip()
        
        # Check for invalid patterns
        invalid_patterns = [
            r'^[»«]$',  # Just arrows
            r'^[A-Za-z]+@[A-Za-z]+\.[A-Za-z]+$',  # Email addresses
            r'^https?://',  # URLs
            r'^<[^>]+>$',  # HTML tags
            r'^[0-9]+$',  # Just numbers
            r'^[^A-Za-z]*$',  # No letters
        ]
        
        import re
        for pattern in invalid_patterns:
            if re.match(pattern, amenity):
                return False
        
        # Check length
        if len(amenity) < 2 or len(amenity) > 100:
            return False
        
        return True
    
    def extract_spider_specific_media_links(self, response: Response) -> List[Dict[str, str]]:
        """Extract Selene-specific media links with deduplication"""
        selector = response.selector
        media_links = []
        seen_urls = set()
        
        # Look for brochure links (limit to 2)
        brochure_links = selector.css('a[href*="brochure"], a[href*=".pdf"]::attr(href)').getall()
        for link in brochure_links[:2]:
            if link and link not in seen_urls and self.is_valid_media_url(link):
                media_links.append({
                    'type': 'brochure',
                    'url': link,
                    'caption': 'Project Brochure'
                })
                seen_urls.add(link)
        
        # Look for virtual tour links (limit to 3)
        vr_links = selector.css('a[href*="virtual"], a[href*="tour"], a[href*="vr"]::attr(href)').getall()
        for link in vr_links[:3]:
            if link and link not in seen_urls and self.is_valid_media_url(link):
                media_links.append({
                    'type': 'vr',
                    'url': link,
                    'caption': 'Virtual Tour'
                })
                seen_urls.add(link)
        
        # Look for floorplan links (limit to 2)
        floorplan_links = selector.css('a[href*="floorplan"], a[href*="layout"]::attr(href)').getall()
        for link in floorplan_links[:2]:
            if link and link not in seen_urls and self.is_valid_media_url(link):
                media_links.append({
                    'type': 'floorplan',
                    'url': link,
                    'caption': 'Floorplans'
                })
                seen_urls.add(link)
        
        # Look for image galleries (limit to 5 best images)
        image_links = selector.css('.gallery img::attr(src), .images img::attr(src), .carousel img::attr(src)').getall()
        for link in image_links[:5]:
            if link and link not in seen_urls and self.is_valid_media_url(link):
                media_links.append({
                    'type': 'image',
                    'url': link,
                    'caption': 'Project Image'
                })
                seen_urls.add(link)
        
        return media_links
    
    def is_valid_media_url(self, url: str) -> bool:
        """Check if media URL is valid"""
        if not url or not isinstance(url, str):
            return False
        
        # Skip invalid URLs
        invalid_patterns = [
            '#elementor-action',
            'javascript:',
            'mailto:',
            'tel:',
            'data:',
            'about:blank'
        ]
        
        for pattern in invalid_patterns:
            if pattern in url.lower():
                return False
        
        # Must be a proper URL
        return url.startswith(('http://', 'https://', '/'))
