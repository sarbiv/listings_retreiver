"""
Base spider for Tier A (official project pages)
"""
import scrapy
import structlog
from typing import Dict, Any, List
from scrapy.http import Response
from ..utils.html import (
    text_or_none, extract_json_ld, extract_contact_info, 
    extract_media_links, extract_amenities, clean_text
)
from ..utils.selectors import extract_project_info, find_units_on_page, extract_unit_info

logger = structlog.get_logger()

class BaseTierASpider(scrapy.Spider):
    """Base spider for official project pages"""
    
    name = 'base_tier_a'
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS': 1,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 0.5,
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_pages = int(kwargs.get('max_pages', 50))
        self.pages_crawled = 0
    
    def parse(self, response: Response):
        """Parse project page"""
        try:
            self.pages_crawled += 1
            
            if self.pages_crawled > self.max_pages:
                logger.info("Reached max pages limit", max_pages=self.max_pages)
                return
            
            # Extract project information
            project_data = self.extract_project_data(response)
            
            # Extract units
            units_data = self.extract_units_data(response)
            
            # Extract amenities
            amenities_data = self.extract_amenities_data(response)
            
            # Extract media links
            media_links_data = self.extract_media_links_data(response)
            
            # Extract source information
            source_data = {
                'source_name': self.name,
                'source_url': response.url,
                'robots_ok': True,
                'tos_ok': True
            }
            
            # Create item
            item = {
                'project': project_data,
                'units': units_data,
                'amenities': amenities_data,
                'media_links': media_links_data,
                'source': source_data
            }
            
            yield item
            
        except Exception as e:
            logger.error("Error parsing project page", url=response.url, error=str(e))
    
    def extract_project_data(self, response: Response) -> Dict[str, Any]:
        """Extract project data from response"""
        selector = response.selector
        
        # Use common selectors first
        project_data = extract_project_info(selector)
        
        # Override with spider-specific extraction
        project_data.update(self.extract_spider_specific_project_data(response))
        
        # Extract from JSON-LD if available
        json_ld_data = extract_json_ld(selector)
        if json_ld_data:
            project_data.update(self.extract_from_json_ld(json_ld_data))
        
        # Extract contact information
        contact_info = extract_contact_info(selector)
        project_data.update(contact_info)
        
        # Clean and validate data
        project_data = self.clean_project_data(project_data)
        
        return project_data
    
    def extract_spider_specific_project_data(self, response: Response) -> Dict[str, Any]:
        """Override in subclasses for spider-specific extraction"""
        return {}
    
    def extract_from_json_ld(self, json_ld_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract project data from JSON-LD structured data"""
        project_data = {}
        
        for data in json_ld_data:
            if data.get('@type') in ['RealEstateAgent', 'Organization', 'Place']:
                # Extract address information
                if 'address' in data:
                    address = data['address']
                    if isinstance(address, dict):
                        project_data['address'] = address.get('streetAddress', '')
                        project_data['city'] = address.get('addressLocality', '')
                        project_data['country'] = address.get('addressCountry', '')
                    elif isinstance(address, str):
                        project_data['address'] = address
                
                # Extract contact information
                if 'email' in data:
                    project_data['contact_email'] = data['email']
                if 'telephone' in data:
                    project_data['phone'] = data['telephone']
                if 'url' in data:
                    project_data['website_url'] = data['url']
                
                # Extract name
                if 'name' in data:
                    project_data['name'] = data['name']
        
        return project_data
    
    def extract_units_data(self, response: Response) -> List[Dict[str, Any]]:
        """Extract units data from response"""
        selector = response.selector
        units_data = []
        
        # Find unit elements
        unit_elements = find_units_on_page(selector)
        
        if unit_elements:
            # Extract individual units
            for unit_element in unit_elements:
                unit_data = extract_unit_info(unit_element)
                unit_data = self.clean_unit_data(unit_data)
                if unit_data:
                    units_data.append(unit_data)
        else:
            # No specific units found, create aggregated unit
            unit_data = self.create_aggregated_unit(response)
            if unit_data:
                units_data.append(unit_data)
        
        return units_data
    
    def create_aggregated_unit(self, response: Response) -> Dict[str, Any]:
        """Create aggregated unit when no specific units are found"""
        selector = response.selector
        
        # Try to extract price information
        price_text = text_or_none(selector, '.price::text, .starting-price::text, .cost::text')
        
        unit_data = {
            'unit_name': 'Various',
            'price_note': 'Price on request' if not price_text else None
        }
        
        if price_text:
            from ..utils.html import extract_price_from_text
            price_info = extract_price_from_text(price_text)
            if price_info:
                unit_data.update(price_info)
        
        return unit_data
    
    def extract_amenities_data(self, response: Response) -> List[str]:
        """Extract amenities data from response"""
        selector = response.selector
        amenities = extract_amenities(selector)
        
        # Add spider-specific amenities
        spider_amenities = self.extract_spider_specific_amenities(response)
        amenities.extend(spider_amenities)
        
        # Remove duplicates and clean
        amenities = list(set(amenities))
        amenities = [clean_text(a) for a in amenities if a and len(a) > 2]
        
        return amenities[:20]  # Limit to 20 amenities
    
    def extract_spider_specific_amenities(self, response: Response) -> List[str]:
        """Override in subclasses for spider-specific amenity extraction"""
        return []
    
    def extract_media_links_data(self, response: Response) -> List[Dict[str, str]]:
        """Extract media links data from response"""
        selector = response.selector
        media_links = extract_media_links(selector)
        
        # Add spider-specific media links
        spider_media = self.extract_spider_specific_media_links(response)
        media_links.extend(spider_media)
        
        return media_links
    
    def extract_spider_specific_media_links(self, response: Response) -> List[Dict[str, str]]:
        """Override in subclasses for spider-specific media extraction"""
        return []
    
    def clean_project_data(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and validate project data"""
        cleaned = {}
        
        for key, value in project_data.items():
            if value is None:
                cleaned[key] = None
                continue
            
            if isinstance(value, str):
                cleaned[key] = clean_text(value)
            else:
                cleaned[key] = value
        
        # Ensure required fields
        if not cleaned.get('name'):
            cleaned['name'] = 'Unknown Project'
        
        return cleaned
    
    def clean_unit_data(self, unit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and validate unit data"""
        cleaned = {}
        
        for key, value in unit_data.items():
            if value is None:
                cleaned[key] = None
                continue
            
            if isinstance(value, str):
                cleaned[key] = clean_text(value)
            else:
                cleaned[key] = value
        
        return cleaned
