"""
Tests for HTML parsing utilities
"""
import pytest
from scrapy import Selector
from scraper.spiders.utils.html import (
    text_or_none, extract_json_ld, extract_contact_info,
    extract_media_links, extract_amenities, clean_text,
    extract_price_from_text
)

class TestHTMLParsing:
    """Test cases for HTML parsing utilities"""
    
    def test_text_or_none(self):
        """Test text extraction with fallback"""
        html = '<div class="test">Hello World</div>'
        selector = Selector(text=html)
        
        # Test successful extraction
        result = text_or_none(selector, '.test::text')
        assert result == "Hello World"
        
        # Test failed extraction
        result = text_or_none(selector, '.nonexistent::text')
        assert result is None
    
    def test_extract_contact_info(self):
        """Test contact information extraction"""
        html = '''
        <div>
            <a href="mailto:contact@example.com">Contact Us</a>
            <a href="tel:+1234567890">Call Us</a>
            <a href="/contact">Contact Form</a>
        </div>
        '''
        selector = Selector(text=html)
        
        contact_info = extract_contact_info(selector)
        assert contact_info['email'] == 'contact@example.com'
        assert contact_info['phone'] == '+1234567890'
        assert contact_info['inquiry_url'] == '/contact'
    
    def test_extract_media_links(self):
        """Test media links extraction"""
        html = '''
        <div>
            <a href="/brochure.pdf">Download Brochure</a>
            <a href="/virtual-tour">Virtual Tour</a>
            <a href="/floorplans">Floorplans</a>
            <img src="/image1.jpg" alt="Project Image">
        </div>
        '''
        selector = Selector(text=html)
        
        media_links = extract_media_links(selector)
        assert len(media_links) >= 4
        
        # Check for brochure
        brochure_links = [link for link in media_links if link['type'] == 'brochure']
        assert len(brochure_links) >= 1
        
        # Check for VR
        vr_links = [link for link in media_links if link['type'] == 'vr']
        assert len(vr_links) >= 1
        
        # Check for floorplan
        floorplan_links = [link for link in media_links if link['type'] == 'floorplan']
        assert len(floorplan_links) >= 1
        
        # Check for images
        image_links = [link for link in media_links if link['type'] == 'image']
        assert len(image_links) >= 1
    
    def test_extract_amenities(self):
        """Test amenities extraction"""
        html = '''
        <div>
            <ul class="amenities">
                <li>Swimming Pool</li>
                <li>Gym</li>
                <li>Concierge Service</li>
            </ul>
            <p>This luxury development features a spa and rooftop deck.</p>
        </div>
        '''
        selector = Selector(text=html)
        
        amenities = extract_amenities(selector)
        assert 'Swimming Pool' in amenities
        assert 'Gym' in amenities
        assert 'Concierge Service' in amenities
        assert 'Spa' in amenities
        assert 'Rooftop Deck' in amenities
    
    def test_clean_text(self):
        """Test text cleaning"""
        assert clean_text("  Hello   World  ") == "Hello World"
        assert clean_text("Multiple    spaces") == "Multiple spaces"
        assert clean_text("") == ""
        assert clean_text(None) == ""
    
    def test_extract_price_from_text(self):
        """Test price extraction from text"""
        # Test various price formats
        price_info = extract_price_from_text("$1,200,000")
        assert price_info['value'] == 1200000.0
        assert price_info['currency'] == 'USD'
        
        price_info = extract_price_from_text("£500,000")
        assert price_info['value'] == 500000.0
        assert price_info['currency'] == 'GBP'
        
        price_info = extract_price_from_text("From $1,000,000")
        assert price_info['value'] == 1000000.0
        assert price_info['note'] == 'From'
        
        price_info = extract_price_from_text("Price on request")
        assert price_info['value'] is None
        assert price_info['note'] == 'Price on request'
