"""
Spider for Pier Sixty-Six Residences (Fort Lauderdale)
"""
import scrapy
import structlog
from typing import Dict, Any, List
from scrapy.http import Response
from .base_spider import BaseTierASpider
from ..utils.html import text_or_none, clean_text

logger = structlog.get_logger()

class PierSixtySixSpider(BaseTierASpider):
    """Spider for Pier Sixty-Six Residences"""
    
    name = 'pier_sixty_six'
    allowed_domains = ['piersixtysixresidences.com']
    start_urls = ['https://piersixtysixresidences.com/']
    
    def extract_spider_specific_project_data(self, response: Response) -> Dict[str, Any]:
        """Extract Pier Sixty-Six specific project data"""
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
        """Extract Pier Sixty-Six specific amenities"""
        selector = response.selector
        amenities = []
        
        # Look for specific amenity sections
        amenity_sections = selector.css('.amenities, .features, .facilities, .amenity-list')
        
        for section in amenity_sections:
            amenity_items = section.css('li::text, .amenity::text, .feature::text').getall()
            for item in amenity_items:
                if item and len(item.strip()) > 2:
                    amenities.append(clean_text(item))
        
        # Look for specific luxury amenities
        luxury_amenities = [
            'Waterfront Location',
            'Marina Access',
            'Resort-Style Pool',
            'Fitness Center',
            'Concierge Service',
            'Valet Parking',
            'Rooftop Deck',
            'Spa Services',
            'Private Beach Access',
            'Boat Slips'
        ]
        
        page_text = selector.get().lower()
        for amenity in luxury_amenities:
            if amenity.lower() in page_text:
                amenities.append(amenity)
        
        return amenities
    
    def extract_spider_specific_media_links(self, response: Response) -> List[Dict[str, str]]:
        """Extract Pier Sixty-Six specific media links"""
        selector = response.selector
        media_links = []
        
        # Look for brochure links
        brochure_links = selector.css('a[href*="brochure"], a[href*=".pdf"]::attr(href)').getall()
        for link in brochure_links:
            media_links.append({
                'type': 'brochure',
                'url': link,
                'caption': 'Project Brochure'
            })
        
        # Look for virtual tour links
        vr_links = selector.css('a[href*="virtual"], a[href*="tour"], a[href*="vr"]::attr(href)').getall()
        for link in vr_links:
            media_links.append({
                'type': 'vr',
                'url': link,
                'caption': 'Virtual Tour'
            })
        
        # Look for floorplan links
        floorplan_links = selector.css('a[href*="floorplan"], a[href*="layout"]::attr(href)').getall()
        for link in floorplan_links:
            media_links.append({
                'type': 'floorplan',
                'url': link,
                'caption': 'Floorplans'
            })
        
        # Look for image galleries
        image_links = selector.css('.gallery img::attr(src), .images img::attr(src)').getall()
        for link in image_links[:10]:  # Limit to first 10 images
            media_links.append({
                'type': 'image',
                'url': link,
                'caption': 'Project Image'
            })
        
        return media_links
