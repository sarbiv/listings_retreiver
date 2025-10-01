"""
Tests for data cleaning and normalization
"""
import pytest
from scraper.pipelines.clean_normalize import CleanNormalizePipeline

class TestCleanNormalizePipeline:
    """Test cases for cleaning and normalization pipeline"""
    
    def setup_method(self):
        """Setup test pipeline"""
        self.pipeline = CleanNormalizePipeline()
    
    def test_clean_text(self):
        """Test text cleaning"""
        # Test basic cleaning
        assert self.pipeline._clean_text("  Hello   World  ") == "Hello World"
        assert self.pipeline._clean_text("Multiple    spaces") == "Multiple spaces"
        assert self.pipeline._clean_text("") == ""
        assert self.pipeline._clean_text(None) == ""
    
    def test_parse_size(self):
        """Test size parsing"""
        # Test various size formats
        assert self.pipeline._parse_size("1,200 sq ft") == 1200.0
        assert self.pipeline._parse_size("120 m²") == 120.0
        assert self.pipeline._parse_size("2,500.5") == 2500.5
        assert self.pipeline._parse_size("") is None
        assert self.pipeline._parse_size(None) is None
    
    def test_parse_price(self):
        """Test price parsing"""
        # Test various price formats
        price_data = self.pipeline._parse_price("$1,200,000")
        assert price_data['value'] == 1200000.0
        assert price_data['currency'] == 'USD'
        
        price_data = self.pipeline._parse_price("£500,000")
        assert price_data['value'] == 500000.0
        assert price_data['currency'] == 'GBP'
        
        price_data = self.pipeline._parse_price("AED 2,500,000")
        assert price_data['value'] == 2500000.0
        assert price_data['currency'] == 'AED'
        
        price_data = self.pipeline._parse_price("From $1,000,000")
        assert price_data['value'] == 1000000.0
        assert price_data['note'] == 'From'
        
        price_data = self.pipeline._parse_price("Price on request")
        assert price_data['value'] is None
        assert price_data['note'] == 'Price on request'
    
    def test_parse_bedrooms(self):
        """Test bedroom parsing"""
        assert self.pipeline._parse_bedrooms("2") == 2.0
        assert self.pipeline._parse_bedrooms("studio") == 0.0
        assert self.pipeline._parse_bedrooms("3.5") == 3.5
        assert self.pipeline._parse_bedrooms("") is None
    
    def test_parse_bathrooms(self):
        """Test bathroom parsing"""
        assert self.pipeline._parse_bathrooms("2") == 2.0
        assert self.pipeline._parse_bathrooms("2.5") == 2.5
        assert self.pipeline._parse_bathrooms("") is None
    
    def test_normalize_status(self):
        """Test status normalization"""
        assert self.pipeline._normalize_status("pre-construction") == "planned"
        assert self.pipeline._normalize_status("under construction") == "under_construction"
        assert self.pipeline._normalize_status("completed") == "completed"
        assert self.pipeline._normalize_status("unknown status") == "unknown"
    
    def test_clean_address(self):
        """Test address cleaning"""
        address = "123 main street, new york, ny"
        cleaned = self.pipeline._clean_address(address)
        assert cleaned == "123 Main Street, New York, Ny"
    
    def test_clean_url(self):
        """Test URL cleaning"""
        assert self.pipeline._clean_url("example.com") == "https://example.com"
        assert self.pipeline._clean_url("https://example.com") == "https://example.com"
        assert self.pipeline._clean_url("") == ""
