"""
Cleaning and normalization pipeline for luxury development scraper
"""
import re
import structlog
from typing import Any, Dict, Optional, Union
from scrapy import Item
from scrapy.exceptions import DropItem
import yaml
from pathlib import Path

logger = structlog.get_logger()

class CleanNormalizePipeline:
    """Pipeline for cleaning and normalizing scraped data"""
    
    def __init__(self):
        self.currency_symbols = {}
        self.status_mappings = {}
        self._load_config()
    
    def _load_config(self):
        """Load configuration from YAML file"""
        config_path = Path(__file__).parent.parent / 'config.yaml'
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                self.currency_symbols = config.get('currency_symbols', {})
                self.status_mappings = config.get('status_mappings', {})
        except Exception as e:
            logger.warning("Could not load config file", error=str(e))
    
    def process_item(self, item: Item, spider) -> Item:
        """Process item through cleaning pipeline"""
        try:
            # Clean project data
            if 'project' in item:
                item['project'] = self._clean_project(item['project'])
            
            # Clean units data
            if 'units' in item:
                item['units'] = [self._clean_unit(unit) for unit in item['units']]
            
            # Clean amenities
            if 'amenities' in item:
                item['amenities'] = [self._clean_amenity(amenity) for amenity in item['amenities']]
            
            # Clean media links
            if 'media_links' in item:
                item['media_links'] = [self._clean_media_link(media) for media in item['media_links']]
            
            return item
            
        except Exception as e:
            logger.error("Error in cleaning pipeline", error=str(e), item=dict(item))
            raise DropItem(f"Cleaning failed: {e}")
    
    def _clean_project(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """Clean project data"""
        cleaned = {}
        
        for key, value in project.items():
            if value is None:
                cleaned[key] = None
                continue
                
            if isinstance(value, str):
                cleaned[key] = self._clean_text(value)
            else:
                cleaned[key] = value
        
        # Normalize status
        if cleaned.get('status'):
            cleaned['status'] = self._normalize_status(cleaned['status'])
        
        # Clean address
        if cleaned.get('address'):
            cleaned['address'] = self._clean_address(cleaned['address'])
        
        # Clean website URL
        if cleaned.get('website_url'):
            cleaned['website_url'] = self._clean_url(cleaned['website_url'])
        
        return cleaned
    
    def _clean_unit(self, unit: Dict[str, Any]) -> Dict[str, Any]:
        """Clean unit data"""
        cleaned = {}
        
        for key, value in unit.items():
            if value is None:
                cleaned[key] = None
                continue
                
            if isinstance(value, str):
                cleaned[key] = self._clean_text(value)
            else:
                cleaned[key] = value
        
        # Parse size fields
        if cleaned.get('size_sqft'):
            cleaned['size_sqft'] = self._parse_size(cleaned['size_sqft'])
        
        if cleaned.get('size_sqm'):
            cleaned['size_sqm'] = self._parse_size(cleaned['size_sqm'])
        
        # Parse price
        if cleaned.get('price_local_value'):
            price_data = self._parse_price(cleaned['price_local_value'])
            if price_data:
                cleaned['price_local_value'] = price_data['value']
                cleaned['price_local_currency'] = price_data['currency']
                cleaned['price_note'] = price_data['note']
        
        # Parse bedrooms/bathrooms
        if cleaned.get('bedrooms'):
            cleaned['bedrooms'] = self._parse_bedrooms(cleaned['bedrooms'])
        
        if cleaned.get('bathrooms'):
            cleaned['bathrooms'] = self._parse_bathrooms(cleaned['bathrooms'])
        
        return cleaned
    
    def _clean_amenity(self, amenity: Union[str, Dict[str, Any]]) -> str:
        """Clean amenity data"""
        if isinstance(amenity, dict):
            amenity = amenity.get('amenity', '')
        
        if not amenity:
            return ''
        
        return self._clean_text(str(amenity))
    
    def _clean_media_link(self, media: Dict[str, Any]) -> Dict[str, Any]:
        """Clean media link data"""
        cleaned = {}
        
        for key, value in media.items():
            if value is None:
                cleaned[key] = None
                continue
                
            if isinstance(value, str):
                cleaned[key] = self._clean_text(value)
            else:
                cleaned[key] = value
        
        # Clean URL
        if cleaned.get('url'):
            cleaned['url'] = self._clean_url(cleaned['url'])
        
        return cleaned
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ''
        
        # Strip whitespace and collapse multiple spaces
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove extra whitespace around punctuation
        text = re.sub(r'\s+([,.!?;:])', r'\1', text)
        
        return text
    
    def _clean_address(self, address: str) -> str:
        """Clean address with basic title case"""
        if not address:
            return ''
        
        # Basic title case (preserve some exceptions)
        address = self._clean_text(address)
        words = address.split()
        title_words = []
        
        for word in words:
            # Don't capitalize common prepositions/articles
            if word.lower() in ['of', 'the', 'and', 'in', 'on', 'at', 'to', 'for', 'with', 'by']:
                title_words.append(word.lower())
            else:
                title_words.append(word.capitalize())
        
        return ' '.join(title_words)
    
    def _clean_url(self, url: str) -> str:
        """Clean and normalize URL"""
        if not url:
            return ''
        
        url = url.strip()
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        return url
    
    def _normalize_status(self, status: str) -> str:
        """Normalize project status"""
        if not status:
            return 'unknown'
        
        status_lower = status.lower().strip()
        
        # Check mappings
        for key, value in self.status_mappings.items():
            if key.lower() in status_lower:
                return value
        
        return 'unknown'
    
    def _parse_size(self, size_text: Union[str, float]) -> Optional[float]:
        """Parse size from text like '1,200 sq ft' or '120 m²'"""
        if isinstance(size_text, (int, float)):
            return float(size_text)
        
        if not size_text:
            return None
        
        # Remove commas and normalize
        size_text = str(size_text).replace(',', '').strip()
        
        # Extract number
        match = re.search(r'(\d+(?:\.\d+)?)', size_text)
        if match:
            return float(match.group(1))
        
        return None
    
    def _parse_price(self, price_text: Union[str, float]) -> Optional[Dict[str, Any]]:
        """Parse price from text like '$1,200,000' or 'AED 2,500,000'"""
        if isinstance(price_text, (int, float)):
            return {'value': float(price_text), 'currency': 'USD', 'note': None}
        
        if not price_text:
            return None
        
        price_text = str(price_text).strip()
        
        # Extract currency and value
        currency = None
        value = None
        note = None
        
        # Check for currency symbols
        for symbol, iso_code in self.currency_symbols.items():
            if symbol in price_text:
                currency = iso_code
                # Remove currency symbol
                price_text = price_text.replace(symbol, '').strip()
                break
        
        # Extract numeric value
        match = re.search(r'(\d+(?:,\d{3})*(?:\.\d+)?)', price_text)
        if match:
            value_str = match.group(1).replace(',', '')
            value = float(value_str)
        
        # Check for notes like "From", "Price on request"
        if 'from' in price_text.lower():
            note = 'From'
        elif 'request' in price_text.lower() or 'contact' in price_text.lower():
            note = 'Price on request'
            value = None
        
        if value is None and currency is None:
            return None
        
        return {
            'value': value,
            'currency': currency or 'USD',
            'note': note
        }
    
    def _parse_bedrooms(self, bedrooms_text: Union[str, float]) -> Optional[float]:
        """Parse bedrooms from text like '2' or 'studio'"""
        if isinstance(bedrooms_text, (int, float)):
            return float(bedrooms_text)
        
        if not bedrooms_text:
            return None
        
        bedrooms_text = str(bedrooms_text).lower().strip()
        
        # Handle studio
        if 'studio' in bedrooms_text:
            return 0.0
        
        # Extract number
        match = re.search(r'(\d+(?:\.\d+)?)', bedrooms_text)
        if match:
            return float(match.group(1))
        
        return None
    
    def _parse_bathrooms(self, bathrooms_text: Union[str, float]) -> Optional[float]:
        """Parse bathrooms from text like '2.5' or '2'"""
        if isinstance(bathrooms_text, (int, float)):
            return float(bathrooms_text)
        
        if not bathrooms_text:
            return None
        
        # Extract number
        match = re.search(r'(\d+(?:\.\d+)?)', str(bathrooms_text))
        if match:
            return float(match.group(1))
        
        return None
