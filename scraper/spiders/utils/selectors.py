"""
CSS/XPath selectors for luxury development scraper
"""
from typing import Dict, List, Optional
from scrapy import Selector

# Common selectors for project information
PROJECT_SELECTORS = {
    'name': [
        'h1::text',
        '.project-title::text',
        '.development-name::text',
        '.property-name::text',
        'title::text'
    ],
    'developer_name': [
        '.developer::text',
        '.developer-name::text',
        '.builder::text',
        '.company::text',
        '[data-developer]::attr(data-developer)'
    ],
    'description': [
        '.description::text',
        '.project-description::text',
        '.overview::text',
        '.summary::text',
        'meta[name="description"]::attr(content)'
    ],
    'address': [
        '.address::text',
        '.location::text',
        '.project-address::text',
        '[itemprop="address"]::text',
        '.contact-address::text'
    ],
    'city': [
        '.city::text',
        '.location-city::text',
        '[data-city]::attr(data-city)',
        '.address .city::text'
    ],
    'country': [
        '.country::text',
        '.location-country::text',
        '[data-country]::attr(data-country)',
        '.address .country::text'
    ],
    'status': [
        '.status::text',
        '.project-status::text',
        '.phase::text',
        '.construction-status::text',
        '[data-status]::attr(data-status)'
    ],
    'est_completion': [
        '.completion::text',
        '.completion-date::text',
        '.delivery::text',
        '.ready::text',
        '[data-completion]::attr(data-completion)'
    ],
    'website_url': [
        '.website::attr(href)',
        '.project-website::attr(href)',
        '.official-site::attr(href)',
        'a[href*="www"]::attr(href)'
    ]
}

# Common selectors for unit information
UNIT_SELECTORS = {
    'unit_name': [
        '.unit-name::text',
        '.apartment-name::text',
        '.residence-name::text',
        '.suite-name::text'
    ],
    'bedrooms': [
        '.bedrooms::text',
        '.beds::text',
        '.bed::text',
        '[data-bedrooms]::attr(data-bedrooms)'
    ],
    'bathrooms': [
        '.bathrooms::text',
        '.baths::text',
        '.bath::text',
        '[data-bathrooms]::attr(data-bathrooms)'
    ],
    'size_sqft': [
        '.size::text',
        '.sqft::text',
        '.square-feet::text',
        '.area::text',
        '[data-size]::attr(data-size)'
    ],
    'price_local_value': [
        '.price::text',
        '.cost::text',
        '.value::text',
        '.starting-price::text',
        '[data-price]::attr(data-price)'
    ],
    'floor': [
        '.floor::text',
        '.level::text',
        '.storey::text',
        '[data-floor]::attr(data-floor)'
    ],
    'exposure': [
        '.exposure::text',
        '.view::text',
        '.orientation::text',
        '.direction::text'
    ],
    'availability_status': [
        '.availability::text',
        '.status::text',
        '.available::text',
        '.sold::text',
        '[data-availability]::attr(data-availability)'
    ]
}

def get_text_by_selectors(selector: Selector, field_name: str, selectors_dict: Dict[str, List[str]]) -> Optional[str]:
    """Try multiple selectors for a field and return first match"""
    selectors = selectors_dict.get(field_name, [])
    
    for sel in selectors:
        try:
            if '::attr(' in sel:
                # Attribute selector
                element_sel, attr_sel = sel.split('::attr(')
                attr_name = attr_sel.rstrip(')')
                result = selector.css(element_sel).css(f'::attr({attr_name})').get()
            else:
                # Text selector
                result = selector.css(sel).get()
            
            if result and result.strip():
                return result.strip()
        except Exception:
            continue
    
    return None

def extract_project_info(selector: Selector) -> Dict[str, Optional[str]]:
    """Extract project information using common selectors"""
    project_info = {}
    
    for field in PROJECT_SELECTORS.keys():
        project_info[field] = get_text_by_selectors(selector, field, PROJECT_SELECTORS)
    
    return project_info

def extract_unit_info(selector: Selector) -> Dict[str, Optional[str]]:
    """Extract unit information using common selectors"""
    unit_info = {}
    
    for field in UNIT_SELECTORS.keys():
        unit_info[field] = get_text_by_selectors(selector, field, UNIT_SELECTORS)
    
    return unit_info

def find_units_on_page(selector: Selector) -> List[Selector]:
    """Find unit elements on page"""
    unit_selectors = [
        '.unit',
        '.apartment',
        '.residence',
        '.suite',
        '.floorplan',
        '.unit-item',
        '.property-unit',
        '[data-unit]',
        '.unit-card',
        '.apartment-card'
    ]
    
    units = []
    for sel in unit_selectors:
        found_units = selector.css(sel)
        if found_units:
            units.extend(found_units)
    
    return units

def find_amenities_on_page(selector: Selector) -> List[Selector]:
    """Find amenity elements on page"""
    amenity_selectors = [
        '.amenities',
        '.features',
        '.facilities',
        '.amenity-list',
        '.feature-list',
        '.facility-list',
        '.amenities ul li',
        '.features ul li',
        '.facilities ul li'
    ]
    
    amenities = []
    for sel in amenity_selectors:
        found_amenities = selector.css(sel)
        if found_amenities:
            amenities.extend(found_amenities)
    
    return amenities
