"""
HTML parsing utilities for luxury development scraper
"""
import re
from typing import Optional, List, Dict, Any
from scrapy import Selector
import structlog

logger = structlog.get_logger()

def text_or_none(node: Selector, selector: str) -> Optional[str]:
    """Extract text from selector or return None if not found"""
    try:
        text = node.css(selector).get()
        if text:
            return text.strip()
        return None
    except Exception as e:
        logger.debug("Error extracting text", selector=selector, error=str(e))
        return None

def extract_json_ld(selector: Selector) -> List[Dict[str, Any]]:
    """Extract JSON-LD structured data from page"""
    json_ld_data = []
    
    try:
        json_ld_scripts = selector.css('script[type="application/ld+json"]::text').getall()
        
        for script_content in json_ld_scripts:
            try:
                import json
                data = json.loads(script_content)
                if isinstance(data, list):
                    json_ld_data.extend(data)
                else:
                    json_ld_data.append(data)
            except json.JSONDecodeError:
                continue
                
    except Exception as e:
        logger.debug("Error extracting JSON-LD", error=str(e))
    
    return json_ld_data

def extract_contact_info(selector: Selector) -> Dict[str, Optional[str]]:
    """Extract contact information from page"""
    contact_info = {
        'email': None,
        'phone': None,
        'inquiry_url': None
    }
    
    try:
        # Look for email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        page_text = selector.get()
        email_matches = re.findall(email_pattern, page_text)
        if email_matches:
            contact_info['email'] = email_matches[0]
        
        # Look for mailto links
        mailto_links = selector.css('a[href^="mailto:"]::attr(href)').getall()
        if mailto_links:
            contact_info['email'] = mailto_links[0].replace('mailto:', '')
        
        # Look for phone numbers (basic pattern)
        phone_pattern = r'(\+?[\d\s\-\(\)]{10,})'
        phone_matches = re.findall(phone_pattern, page_text)
        if phone_matches:
            contact_info['phone'] = phone_matches[0].strip()
        
        # Look for contact/inquiry forms
        contact_links = selector.css('a[href*="contact"], a[href*="inquiry"], a[href*="enquiry"]::attr(href)').getall()
        if contact_links:
            contact_info['inquiry_url'] = contact_links[0]
        
        # Look for form actions
        form_actions = selector.css('form[action]::attr(action)').getall()
        if form_actions:
            contact_info['inquiry_url'] = form_actions[0]
            
    except Exception as e:
        logger.debug("Error extracting contact info", error=str(e))
    
    return contact_info

def extract_media_links(selector: Selector) -> List[Dict[str, str]]:
    """Extract media links (brochures, VR, floorplans) from page"""
    media_links = []
    
    try:
        # Look for PDF links
        pdf_links = selector.css('a[href*=".pdf"]::attr(href)').getall()
        for link in pdf_links:
            media_links.append({
                'type': 'brochure',
                'url': link,
                'caption': 'Brochure'
            })
        
        # Look for VR/virtual tour links
        vr_keywords = ['virtual', 'tour', 'vr', '3d', '360']
        for keyword in vr_keywords:
            vr_links = selector.css(f'a[href*="{keyword}"], a[href*="{keyword.upper()}"]::attr(href)').getall()
            for link in vr_links:
                media_links.append({
                    'type': 'vr',
                    'url': link,
                    'caption': f'Virtual Tour ({keyword})'
                })
        
        # Look for floorplan links
        floorplan_keywords = ['floorplan', 'floor-plan', 'floor_plan', 'layout']
        for keyword in floorplan_keywords:
            floorplan_links = selector.css(f'a[href*="{keyword}"], a[href*="{keyword.replace("-", "_")}"]::attr(href)').getall()
            for link in floorplan_links:
                media_links.append({
                    'type': 'floorplan',
                    'url': link,
                    'caption': 'Floorplan'
                })
        
        # Look for image galleries
        image_links = selector.css('a[href*=".jpg"], a[href*=".jpeg"], a[href*=".png"], a[href*=".webp"]::attr(href)').getall()
        for link in image_links[:10]:  # Limit to first 10 images
            media_links.append({
                'type': 'image',
                'url': link,
                'caption': 'Project Image'
            })
        
        # Look for video links
        video_links = selector.css('a[href*=".mp4"], a[href*="youtube"], a[href*="vimeo"]::attr(href)').getall()
        for link in video_links:
            media_links.append({
                'type': 'video',
                'url': link,
                'caption': 'Project Video'
            })
            
    except Exception as e:
        logger.debug("Error extracting media links", error=str(e))
    
    return media_links

def extract_amenities(selector: Selector) -> List[str]:
    """Extract amenities from page"""
    amenities = []
    
    try:
        # Common amenity keywords
        amenity_keywords = [
            'pool', 'gym', 'fitness', 'spa', 'concierge', 'parking', 'garage',
            'balcony', 'terrace', 'garden', 'rooftop', 'lounge', 'library',
            'business center', 'meeting room', 'restaurant', 'cafe', 'bar',
            'security', 'doorman', 'elevator', 'air conditioning', 'heating',
            'dishwasher', 'washer', 'dryer', 'marble', 'granite', 'hardwood',
            'marble floors', 'granite countertops', 'stainless steel',
            'ocean view', 'city view', 'waterfront', 'beach access',
            'tennis', 'golf', 'squash', 'basketball', 'soccer'
        ]
        
        page_text = selector.get().lower()
        
        for keyword in amenity_keywords:
            if keyword in page_text:
                amenities.append(keyword.title())
        
        # Also look for structured amenity lists
        amenity_lists = selector.css('ul li, ol li, .amenity, .feature').getall()
        for item in amenity_lists:
            text = Selector(text=item).css('::text').get()
            if text and len(text.strip()) > 3 and len(text.strip()) < 100:
                amenities.append(text.strip().title())
        
        # Remove duplicates and clean up
        amenities = list(set(amenities))
        amenities = [a for a in amenities if a and len(a) > 2]
        
    except Exception as e:
        logger.debug("Error extracting amenities", error=str(e))
    
    return amenities[:20]  # Limit to 20 amenities

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ''
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove HTML entities
    text = re.sub(r'&[a-zA-Z0-9#]+;', ' ', text)
    
    return text

def extract_price_from_text(text: str) -> Optional[Dict[str, Any]]:
    """Extract price information from text"""
    if not text:
        return None
    
    # Currency symbols mapping
    currency_map = {
        '$': 'USD',
        '£': 'GBP',
        '€': 'EUR',
        '₪': 'ILS',
        'AED': 'AED',
        'S$': 'SGD',
        '¥': 'JPY',
        '₹': 'INR'
    }
    
    # Price patterns
    price_patterns = [
        r'(\$|£|€|₪|AED|S\$|¥|₹)\s*([\d,]+(?:\.\d{2})?)',  # Currency symbol + number
        r'([\d,]+(?:\.\d{2})?)\s*(\$|£|€|₪|AED|S\$|¥|₹)',  # Number + currency symbol
        r'from\s+(\$|£|€|₪|AED|S\$|¥|₹)\s*([\d,]+(?:\.\d{2})?)',  # "From $X"
        r'starting\s+at\s+(\$|£|€|₪|AED|S\$|¥|₹)\s*([\d,]+(?:\.\d{2})?)',  # "Starting at $X"
    ]
    
    for pattern in price_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            groups = match.groups()
            if len(groups) == 2:
                currency_symbol = groups[0]
                amount_str = groups[1]
            else:
                continue
            
            try:
                amount = float(amount_str.replace(',', ''))
                currency = currency_map.get(currency_symbol, 'USD')
                
                return {
                    'value': amount,
                    'currency': currency,
                    'note': 'From' if 'from' in text.lower() or 'starting' in text.lower() else None
                }
            except ValueError:
                continue
    
    return None
