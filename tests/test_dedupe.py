"""
Tests for deduplication pipeline
"""
import pytest
from scraper.pipelines.dedupe import DedupePipeline

class TestDedupePipeline:
    """Test cases for deduplication pipeline"""
    
    def setup_method(self):
        """Setup test pipeline"""
        self.pipeline = DedupePipeline()
    
    def test_generate_project_key(self):
        """Test canonical key generation"""
        project_data = {
            'name': 'Luxury Tower',
            'developer_name': 'ABC Developers',
            'city': 'New York',
            'country': 'United States'
        }
        
        key = self.pipeline._generate_project_key(project_data)
        assert key == "luxury-tower-abc-developers-new-york-united-states"
        
        # Test with missing fields
        project_data = {
            'name': 'Luxury Tower',
            'developer_name': '',
            'city': 'New York',
            'country': 'United States'
        }
        
        key = self.pipeline._generate_project_key(project_data)
        assert key == "luxury-tower-new-york-united-states"
    
    def test_generate_project_key_consistency(self):
        """Test that same project data generates same key"""
        project_data = {
            'name': 'Luxury Tower',
            'developer_name': 'ABC Developers',
            'city': 'New York',
            'country': 'United States'
        }
        
        key1 = self.pipeline._generate_project_key(project_data)
        key2 = self.pipeline._generate_project_key(project_data)
        assert key1 == key2
    
    def test_generate_project_key_case_insensitive(self):
        """Test that case doesn't affect key generation"""
        project_data1 = {
            'name': 'Luxury Tower',
            'developer_name': 'ABC Developers',
            'city': 'New York',
            'country': 'United States'
        }
        
        project_data2 = {
            'name': 'luxury tower',
            'developer_name': 'abc developers',
            'city': 'new york',
            'country': 'united states'
        }
        
        key1 = self.pipeline._generate_project_key(project_data1)
        key2 = self.pipeline._generate_project_key(project_data2)
        assert key1 == key2
