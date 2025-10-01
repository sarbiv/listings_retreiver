"""
Base spider for Tier B (regional portals)
"""
import scrapy
import structlog
from typing import Dict, Any, List
from scrapy.http import Response
from ..utils.html import text_or_none, clean_text

logger = structlog.get_logger()

class BaseTierBSpider(scrapy.Spider):
    """Base spider for regional portals"""
    
    name = 'base_tier_b'
    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        'RANDOMIZE_DOWNLOAD_DELAY': 1.0,
        'CONCURRENT_REQUESTS': 1,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 0.3,
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_projects = int(kwargs.get('max_projects', 200))
        self.projects_crawled = 0
    
    def parse(self, response: Response):
        """Parse portal listing page"""
        try:
            # Extract project links from listing page
            project_links = self.extract_project_links(response)
            
            for link in project_links:
                if self.projects_crawled >= self.max_projects:
                    logger.info("Reached max projects limit", max_projects=self.max_projects)
                    break
                
                yield response.follow(link, self.parse_project_page)
            
            # Follow pagination if available
            next_page = self.get_next_page(response)
            if next_page and self.projects_crawled < self.max_projects:
                yield response.follow(next_page, self.parse)
                
        except Exception as e:
            logger.error("Error parsing portal page", url=response.url, error=str(e))
    
    def parse_project_page(self, response: Response):
        """Parse individual project page"""
        try:
            self.projects_crawled += 1
            
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
    
    def extract_project_links(self, response: Response) -> List[str]:
        """Extract project links from listing page - override in subclasses"""
        return []
    
    def get_next_page(self, response: Response) -> str:
        """Get next page URL - override in subclasses"""
        return None
    
    def extract_project_data(self, response: Response) -> Dict[str, Any]:
        """Extract project data from response"""
        selector = response.selector
        
        project_data = {}
        
        # Extract basic project information
        project_data['name'] = text_or_none(selector, 'h1::text, .project-title::text, .development-name::text')
        project_data['developer_name'] = text_or_none(selector, '.developer::text, .builder::text, .company::text')
        project_data['description'] = text_or_none(selector, '.description::text, .overview::text, .summary::text')
        project_data['address'] = text_or_none(selector, '.address::text, .location::text, .project-address::text')
        project_data['city'] = text_or_none(selector, '.city::text, .location-city::text')
        project_data['country'] = text_or_none(selector, '.country::text, .location-country::text')
        project_data['status'] = text_or_none(selector, '.status::text, .phase::text, .construction-status::text')
        project_data['est_completion'] = text_or_none(selector, '.completion::text, .completion-date::text, .delivery::text')
        project_data['website_url'] = text_or_none(selector, '.website::attr(href), .project-website::attr(href), .official-site::attr(href)')
        
        # Set default property type
        project_data['property_type'] = 'Residential'
        
        # Clean and validate data
        project_data = self.clean_project_data(project_data)
        
        return project_data
    
    def extract_units_data(self, response: Response) -> List[Dict[str, Any]]:
        """Extract units data from response"""
        selector = response.selector
        units_data = []
        
        # Look for unit elements
        unit_elements = selector.css('.unit, .apartment, .residence, .suite, .floorplan')
        
        if unit_elements:
            for unit_element in unit_elements:
                unit_data = {
                    'unit_name': text_or_none(unit_element, '.unit-name::text, .apartment-name::text'),
                    'bedrooms': text_or_none(unit_element, '.bedrooms::text, .beds::text'),
                    'bathrooms': text_or_none(unit_element, '.bathrooms::text, .baths::text'),
                    'size_sqft': text_or_none(unit_element, '.size::text, .sqft::text, .square-feet::text'),
                    'price_local_value': text_or_none(unit_element, '.price::text, .cost::text, .value::text'),
                    'floor': text_or_none(unit_element, '.floor::text, .level::text'),
                    'exposure': text_or_none(unit_element, '.exposure::text, .view::text'),
                    'availability_status': text_or_none(unit_element, '.availability::text, .status::text')
                }
                
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
        amenities = []
        
        # Look for amenity sections
        amenity_sections = selector.css('.amenities, .features, .facilities, .amenity-list')
        
        for section in amenity_sections:
            amenity_items = section.css('li::text, .amenity::text, .feature::text').getall()
            for item in amenity_items:
                if item and len(item.strip()) > 2:
                    amenities.append(clean_text(item))
        
        # Remove duplicates and clean
        amenities = list(set(amenities))
        amenities = [a for a in amenities if a and len(a) > 2]
        
        return amenities[:20]  # Limit to 20 amenities
    
    def extract_media_links_data(self, response: Response) -> List[Dict[str, str]]:
        """Extract media links data from response"""
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
