#!/usr/bin/env python3
"""
Data validation and sanity checks for luxury development scraper
"""
import sys
import os
from pathlib import Path
import pandas as pd
import re
from typing import Dict, List, Any, Optional

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scraper.db.io import DatabaseManager
from scraper.db.models import Project, Unit, Amenity, MediaLink, Source

class DataValidator:
    """Validates and cleans scraped data"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.validation_errors = []
        self.cleaning_suggestions = []
    
    def validate_all_data(self):
        """Run all validation checks"""
        print("🔍 Running Data Validation Checks...")
        print("=" * 60)
        
        # Check database connection
        self.validate_database_connection()
        
        # Validate projects
        self.validate_projects()
        
        # Validate units
        self.validate_units()
        
        # Validate amenities
        self.validate_amenities()
        
        # Validate media links
        self.validate_media_links()
        
        # Validate sources
        self.validate_sources()
        
        # Print summary
        self.print_validation_summary()
    
    def validate_database_connection(self):
        """Test database connection and basic stats"""
        try:
            stats = self.db.get_stats()
            print(f"✅ Database Connection: OK")
            print(f"   Projects: {stats['projects']}")
            print(f"   Units: {stats['units']}")
            print(f"   Amenities: {stats['amenities']}")
            print(f"   Media Links: {stats['media_links']}")
            print(f"   Sources: {stats['sources']}")
        except Exception as e:
            print(f"❌ Database Connection: FAILED - {e}")
            self.validation_errors.append(f"Database connection failed: {e}")
    
    def validate_projects(self):
        """Validate project data"""
        print(f"\n🏢 Validating Projects...")
        
        session = self.db.get_session()
        try:
            projects = session.query(Project).all()
            
            if not projects:
                print("   ⚠️  No projects found in database")
                return
            
            for project in projects:
                self.validate_project(project)
                
        finally:
            session.close()
    
    def validate_project(self, project: Project):
        """Validate individual project"""
        errors = []
        warnings = []
        
        # Required fields
        if not project.name or project.name.strip() == "":
            errors.append("Missing project name")
        elif len(project.name) < 3:
            warnings.append("Project name too short")
        
        if not project.city:
            errors.append("Missing city")
        
        if not project.country:
            errors.append("Missing country")
        
        # Data quality checks
        if project.website_url:
            if not self.is_valid_url(project.website_url):
                errors.append(f"Invalid website URL: {project.website_url}")
        
        if project.contact_email:
            if not self.is_valid_email(project.contact_email):
                errors.append(f"Invalid email: {project.contact_email}")
        
        # Check for HTML tags in text fields
        html_fields = ['name', 'description', 'address']
        for field in html_fields:
            value = getattr(project, field, None)
            if value and self.contains_html(value):
                warnings.append(f"HTML tags found in {field}: {value[:50]}...")
        
        # Completeness score
        if project.completeness_score is None:
            warnings.append("Missing completeness score")
        elif project.completeness_score < 0.3:
            warnings.append(f"Low completeness score: {project.completeness_score:.1%}")
        
        # Print results
        if errors:
            print(f"   ❌ Project '{project.name}': {len(errors)} errors")
            for error in errors:
                print(f"      - {error}")
                self.validation_errors.append(f"Project {project.id}: {error}")
        elif warnings:
            print(f"   ⚠️  Project '{project.name}': {len(warnings)} warnings")
            for warning in warnings:
                print(f"      - {warning}")
                self.cleaning_suggestions.append(f"Project {project.id}: {warning}")
        else:
            print(f"   ✅ Project '{project.name}': Valid")
    
    def validate_units(self):
        """Validate unit data"""
        print(f"\n🏠 Validating Units...")
        
        session = self.db.get_session()
        try:
            units = session.query(Unit).all()
            
            if not units:
                print("   ⚠️  No units found in database")
                return
            
            for unit in units:
                self.validate_unit(unit)
                
        finally:
            session.close()
    
    def validate_unit(self, unit: Unit):
        """Validate individual unit"""
        errors = []
        warnings = []
        
        # Check for valid numeric fields
        if unit.bedrooms is not None and (unit.bedrooms < 0 or unit.bedrooms > 20):
            warnings.append(f"Unusual bedroom count: {unit.bedrooms}")
        
        if unit.bathrooms is not None and (unit.bathrooms < 0 or unit.bathrooms > 20):
            warnings.append(f"Unusual bathroom count: {unit.bathrooms}")
        
        if unit.size_sqft is not None and (unit.size_sqft < 100 or unit.size_sqft > 50000):
            warnings.append(f"Unusual size: {unit.size_sqft} sq ft")
        
        if unit.price_local_value is not None and (unit.price_local_value < 1000 or unit.price_local_value > 100000000):
            warnings.append(f"Unusual price: {unit.price_local_value}")
        
        # Check for missing essential data
        if not unit.unit_name:
            warnings.append("Missing unit name")
        
        if not unit.price_local_value and not unit.price_note:
            warnings.append("No price information")
        
        # Print results
        if errors:
            print(f"   ❌ Unit {unit.id}: {len(errors)} errors")
            for error in errors:
                print(f"      - {error}")
        elif warnings:
            print(f"   ⚠️  Unit {unit.id}: {len(warnings)} warnings")
            for warning in warnings:
                print(f"      - {warning}")
        else:
            print(f"   ✅ Unit {unit.id}: Valid")
    
    def validate_amenities(self):
        """Validate amenity data"""
        print(f"\n🏊 Validating Amenities...")
        
        session = self.db.get_session()
        try:
            amenities = session.query(Amenity).all()
            
            if not amenities:
                print("   ⚠️  No amenities found in database")
                return
            
            # Check for invalid amenities
            invalid_amenities = []
            for amenity in amenities:
                if not self.is_valid_amenity(amenity.amenity):
                    invalid_amenities.append(amenity)
            
            if invalid_amenities:
                print(f"   ⚠️  Found {len(invalid_amenities)} invalid amenities:")
                for amenity in invalid_amenities[:10]:  # Show first 10
                    print(f"      - '{amenity.amenity}' (ID: {amenity.id})")
                    self.cleaning_suggestions.append(f"Invalid amenity: '{amenity.amenity}'")
            else:
                print(f"   ✅ All {len(amenities)} amenities are valid")
                
        finally:
            session.close()
    
    def validate_media_links(self):
        """Validate media link data"""
        print(f"\n📸 Validating Media Links...")
        
        session = self.db.get_session()
        try:
            media_links = session.query(MediaLink).all()
            
            if not media_links:
                print("   ⚠️  No media links found in database")
                return
            
            invalid_links = []
            for media in media_links:
                if not self.is_valid_media_link(media):
                    invalid_links.append(media)
            
            if invalid_links:
                print(f"   ⚠️  Found {len(invalid_links)} invalid media links:")
                for media in invalid_links[:10]:  # Show first 10
                    print(f"      - {media.type}: {media.url[:50]}...")
                    self.cleaning_suggestions.append(f"Invalid media link: {media.url}")
            else:
                print(f"   ✅ All {len(media_links)} media links are valid")
                
        finally:
            session.close()
    
    def validate_sources(self):
        """Validate source data"""
        print(f"\n🔗 Validating Sources...")
        
        session = self.db.get_session()
        try:
            sources = session.query(Source).all()
            
            if not sources:
                print("   ⚠️  No sources found in database")
                return
            
            for source in sources:
                if not self.is_valid_url(source.source_url):
                    print(f"   ⚠️  Invalid source URL: {source.source_url}")
                    self.cleaning_suggestions.append(f"Invalid source URL: {source.source_url}")
                else:
                    print(f"   ✅ Source: {source.source_name}")
                    
        finally:
            session.close()
    
    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid"""
        if not url or not isinstance(url, str):
            return False
        
        # Check for HTML tags
        if self.contains_html(url):
            return False
        
        # Check for basic URL pattern
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return bool(url_pattern.match(url))
    
    def is_valid_email(self, email: str) -> bool:
        """Check if email is valid"""
        if not email or not isinstance(email, str):
            return False
        
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        return bool(email_pattern.match(email))
    
    def contains_html(self, text: str) -> bool:
        """Check if text contains HTML tags"""
        if not text or not isinstance(text, str):
            return False
        
        html_pattern = re.compile(r'<[^>]+>')
        return bool(html_pattern.search(text))
    
    def is_valid_amenity(self, amenity: str) -> bool:
        """Check if amenity is valid"""
        if not amenity or not isinstance(amenity, str):
            return False
        
        # Remove whitespace
        amenity = amenity.strip()
        
        # Check for invalid patterns
        invalid_patterns = [
            r'^[»«]$',  # Just arrows
            r'^[A-Za-z]+@[A-Za-z]+\.[A-Za-z]+$',  # Email addresses
            r'^https?://',  # URLs
            r'^<[^>]+>$',  # HTML tags
            r'^[0-9]+$',  # Just numbers
            r'^[^A-Za-z]*$',  # No letters
        ]
        
        for pattern in invalid_patterns:
            if re.match(pattern, amenity):
                return False
        
        # Check length
        if len(amenity) < 2 or len(amenity) > 100:
            return False
        
        return True
    
    def is_valid_media_link(self, media: MediaLink) -> bool:
        """Check if media link is valid"""
        if not media.url or not isinstance(media.url, str):
            return False
        
        # Check for HTML tags
        if self.contains_html(media.url):
            return False
        
        # Check for valid media types
        valid_types = ['image', 'render', 'video', 'vr', 'brochure', 'floorplan']
        if media.type not in valid_types:
            return False
        
        return True
    
    def print_validation_summary(self):
        """Print validation summary"""
        print(f"\n📊 Validation Summary")
        print("=" * 60)
        
        if self.validation_errors:
            print(f"❌ Errors Found: {len(self.validation_errors)}")
            for error in self.validation_errors[:5]:  # Show first 5
                print(f"   - {error}")
            if len(self.validation_errors) > 5:
                print(f"   ... and {len(self.validation_errors) - 5} more")
        else:
            print("✅ No critical errors found")
        
        if self.cleaning_suggestions:
            print(f"\n⚠️  Cleaning Suggestions: {len(self.cleaning_suggestions)}")
            for suggestion in self.cleaning_suggestions[:5]:  # Show first 5
                print(f"   - {suggestion}")
            if len(self.cleaning_suggestions) > 5:
                print(f"   ... and {len(self.cleaning_suggestions) - 5} more")
        else:
            print("✅ No cleaning suggestions")
        
        print(f"\n💡 Next Steps:")
        if self.validation_errors:
            print("   1. Fix critical errors before running spiders")
        if self.cleaning_suggestions:
            print("   2. Review and clean data quality issues")
        print("   3. Re-run validation after fixes")

def main():
    """Run data validation"""
    validator = DataValidator()
    validator.validate_all_data()

if __name__ == '__main__':
    main()
