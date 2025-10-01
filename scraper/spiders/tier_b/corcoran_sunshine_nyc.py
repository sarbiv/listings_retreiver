"""
Spider for Corcoran Sunshine NYC (new developments)
"""
import scrapy
import structlog
from typing import Dict, Any, List
from scrapy.http import Response
from .base_spider import BaseTierBSpider
from ..utils.html import text_or_none, clean_text

logger = structlog.get_logger()

class CorcoranSunshineNycSpider(BaseTierBSpider):
    """Spider for Corcoran Sunshine NYC new developments"""
    
    name = 'corcoran_sunshine_nyc'
    allowed_domains = ['corcoran.com']
    start_urls = ['https://www.corcoran.com/new-developments']
    
    def extract_project_links(self, response: Response) -> List[str]:
        """Extract project links from Corcoran Sunshine listing page"""
        selector = response.selector
        
        # Look for project links
        project_links = selector.css('.project-card a::attr(href), .development-card a::attr(href), .property-card a::attr(href)').getall()
        
        # Also look for specific Corcoran selectors
        if not project_links:
            project_links = selector.css('a[href*="/new-development/"], a[href*="/development/"], a[href*="/project/"]::attr(href)').getall()
        
        # Convert relative URLs to absolute
        absolute_links = []
        for link in project_links:
            if link.startswith('/'):
                absolute_links.append('https://www.corcoran.com' + link)
            elif link.startswith('http'):
                absolute_links.append(link)
        
        return absolute_links
    
    def get_next_page(self, response: Response) -> str:
        """Get next page URL from Corcoran Sunshine pagination"""
        selector = response.selector
        
        # Look for next page link
        next_page = selector.css('.pagination .next::attr(href), .pagination .page-next::attr(href)').get()
        
        if next_page and next_page.startswith('/'):
            return 'https://www.corcoran.com' + next_page
        elif next_page and next_page.startswith('http'):
            return next_page
        
        return None
    
    def extract_project_data(self, response: Response) -> Dict[str, Any]:
        """Extract project data from Corcoran Sunshine project page"""
        selector = response.selector
        
        project_data = {}
        
        # Extract project name
        name = text_or_none(selector, 'h1::text, .project-title::text, .development-name::text')
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
        project_data['city'] = 'New York'
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
        
        # Look for official website link
        official_site = text_or_none(selector, '.official-website::attr(href), .developer-website::attr(href)')
        if official_site:
            project_data['website_url'] = official_site
        
        # Clean and validate data
        project_data = self.clean_project_data(project_data)
        
        return project_data
    
    def extract_amenities_data(self, response: Response) -> List[str]:
        """Extract amenities data from Corcoran Sunshine project page"""
        selector = response.selector
        amenities = []
        
        # Look for amenity sections
        amenity_sections = selector.css('.amenities, .features, .facilities, .amenity-list')
        
        for section in amenity_sections:
            amenity_items = section.css('li::text, .amenity::text, .feature::text').getall()
            for item in amenity_items:
                if item and len(item.strip()) > 2:
                    amenities.append(clean_text(item))
        
        # Look for specific NYC luxury amenities
        luxury_amenities = [
            'Concierge Service',
            'Doorman',
            'Gym',
            'Swimming Pool',
            'Rooftop Deck',
            'Terrace',
            'Balcony',
            'Parking',
            'Storage',
            'Laundry',
            'Dishwasher',
            'Air Conditioning',
            'Heating',
            'Hardwood Floors',
            'Marble Countertops',
            'Stainless Steel Appliances',
            'City View',
            'River View',
            'Park View',
            'High Ceilings',
            'Large Windows',
            'Private Elevator',
            'Wine Cellar',
            'Home Office',
            'Library'
        ]
        
        page_text = selector.get().lower()
        for amenity in luxury_amenities:
            if amenity.lower() in page_text:
                amenities.append(amenity)
        
        # Remove duplicates and clean
        amenities = list(set(amenities))
        amenities = [a for a in amenities if a and len(a) > 2]
        
        return amenities[:20]  # Limit to 20 amenities
