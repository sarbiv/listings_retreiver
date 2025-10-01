#!/usr/bin/env python3
"""
Data cleaning script for luxury development scraper
"""
import sys
import os
from pathlib import Path
import re
from typing import Dict, List, Any, Optional

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scraper.db.io import DatabaseManager
from scraper.db.models import Project, Unit, Amenity, MediaLink, Source

class DataCleaner:
    """Cleans and fixes scraped data"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.cleaning_stats = {
            'projects_cleaned': 0,
            'units_cleaned': 0,
            'amenities_removed': 0,
            'media_links_cleaned': 0,
            'sources_cleaned': 0
        }
    
    def clean_all_data(self):
        """Run all cleaning operations"""
        print("🧹 Starting Data Cleaning...")
        print("=" * 60)
        
        # Clean projects
        self.clean_projects()
        
        # Clean units
        self.clean_units()
        
        # Clean amenities
        self.clean_amenities()
        
        # Clean media links
        self.clean_media_links()
        
        # Clean sources
        self.clean_sources()
        
        # Print summary
        self.print_cleaning_summary()
    
    def clean_projects(self):
        """Clean project data"""
        print(f"\n🏢 Cleaning Projects...")
        
        session = self.db.get_session()
        try:
            projects = session.query(Project).all()
            
            for project in projects:
                cleaned = False
                
                # Clean HTML tags from text fields
                if project.name and self.contains_html(project.name):
                    project.name = self.strip_html(project.name)
                    cleaned = True
                
                if project.description and self.contains_html(project.description):
                    project.description = self.strip_html(project.description)
                    cleaned = True
                
                if project.address and self.contains_html(project.address):
                    project.address = self.strip_html(project.address)
                    cleaned = True
                
                # Clean website URL
                if project.website_url and self.contains_html(project.website_url):
                    project.website_url = self.extract_url_from_html(project.website_url)
                    cleaned = True
                
                # Clean inquiry URL
                if project.inquiry_url and self.contains_html(project.inquiry_url):
                    project.inquiry_url = self.extract_url_from_html(project.inquiry_url)
                    cleaned = True
                
                # Clean contact email
                if project.contact_email:
                    cleaned_email = self.clean_email(project.contact_email)
                    if cleaned_email != project.contact_email:
                        project.contact_email = cleaned_email
                        cleaned = True
                
                if cleaned:
                    self.cleaning_stats['projects_cleaned'] += 1
                    print(f"   ✅ Cleaned project: {project.name}")
            
            session.commit()
            print(f"   📊 Cleaned {self.cleaning_stats['projects_cleaned']} projects")
            
        except Exception as e:
            session.rollback()
            print(f"   ❌ Error cleaning projects: {e}")
        finally:
            session.close()
    
    def clean_units(self):
        """Clean unit data"""
        print(f"\n🏠 Cleaning Units...")
        
        session = self.db.get_session()
        try:
            units = session.query(Unit).all()
            
            for unit in units:
                cleaned = False
                
                # Clean unit name
                if unit.unit_name and self.contains_html(unit.unit_name):
                    unit.unit_name = self.strip_html(unit.unit_name)
                    cleaned = True
                
                # Clean price note
                if unit.price_note and self.contains_html(unit.price_note):
                    unit.price_note = self.strip_html(unit.price_note)
                    cleaned = True
                
                # Clean URLs
                for url_field in ['floorplan_url', 'vr_url', 'brochure_url']:
                    url_value = getattr(unit, url_field)
                    if url_value and self.contains_html(url_value):
                        cleaned_url = self.extract_url_from_html(url_value)
                        setattr(unit, url_field, cleaned_url)
                        cleaned = True
                
                if cleaned:
                    self.cleaning_stats['units_cleaned'] += 1
                    print(f"   ✅ Cleaned unit: {unit.unit_name or f'Unit {unit.id}'}")
            
            session.commit()
            print(f"   📊 Cleaned {self.cleaning_stats['units_cleaned']} units")
            
        except Exception as e:
            session.rollback()
            print(f"   ❌ Error cleaning units: {e}")
        finally:
            session.close()
    
    def clean_amenities(self):
        """Clean amenity data"""
        print(f"\n🏊 Cleaning Amenities...")
        
        session = self.db.get_session()
        try:
            amenities = session.query(Amenity).all()
            amenities_to_remove = []
            
            for amenity in amenities:
                # Check if amenity is invalid
                if not self.is_valid_amenity(amenity.amenity):
                    amenities_to_remove.append(amenity)
                    continue
                
                # Clean HTML tags
                if self.contains_html(amenity.amenity):
                    cleaned_amenity = self.strip_html(amenity.amenity)
                    if self.is_valid_amenity(cleaned_amenity):
                        amenity.amenity = cleaned_amenity
                        print(f"   ✅ Cleaned amenity: {cleaned_amenity}")
                    else:
                        amenities_to_remove.append(amenity)
            
            # Remove invalid amenities
            for amenity in amenities_to_remove:
                session.delete(amenity)
                self.cleaning_stats['amenities_removed'] += 1
                print(f"   🗑️  Removed invalid amenity: '{amenity.amenity}'")
            
            session.commit()
            print(f"   📊 Removed {self.cleaning_stats['amenities_removed']} invalid amenities")
            
        except Exception as e:
            session.rollback()
            print(f"   ❌ Error cleaning amenities: {e}")
        finally:
            session.close()
    
    def clean_media_links(self):
        """Clean media link data"""
        print(f"\n📸 Cleaning Media Links...")
        
        session = self.db.get_session()
        try:
            media_links = session.query(MediaLink).all()
            media_links_to_remove = []
            
            for media in media_links:
                # Check if media link is invalid
                if not self.is_valid_media_link(media):
                    media_links_to_remove.append(media)
                    continue
                
                # Clean HTML tags from URL
                if self.contains_html(media.url):
                    cleaned_url = self.extract_url_from_html(media.url)
                    if cleaned_url and self.is_valid_url(cleaned_url):
                        media.url = cleaned_url
                        self.cleaning_stats['media_links_cleaned'] += 1
                        print(f"   ✅ Cleaned media URL: {cleaned_url[:50]}...")
                    else:
                        media_links_to_remove.append(media)
                
                # Clean caption
                if media.caption and self.contains_html(media.caption):
                    media.caption = self.strip_html(media.caption)
            
            # Remove invalid media links
            for media in media_links_to_remove:
                session.delete(media)
                print(f"   🗑️  Removed invalid media link: {media.url[:50]}...")
            
            session.commit()
            print(f"   📊 Cleaned {self.cleaning_stats['media_links_cleaned']} media links")
            
        except Exception as e:
            session.rollback()
            print(f"   ❌ Error cleaning media links: {e}")
        finally:
            session.close()
    
    def clean_sources(self):
        """Clean source data"""
        print(f"\n🔗 Cleaning Sources...")
        
        session = self.db.get_session()
        try:
            sources = session.query(Source).all()
            
            for source in sources:
                cleaned = False
                
                # Clean source name
                if source.source_name and self.contains_html(source.source_name):
                    source.source_name = self.strip_html(source.source_name)
                    cleaned = True
                
                # Clean source URL
                if source.source_url and self.contains_html(source.source_url):
                    cleaned_url = self.extract_url_from_html(source.source_url)
                    if cleaned_url:
                        source.source_url = cleaned_url
                        cleaned = True
                
                if cleaned:
                    self.cleaning_stats['sources_cleaned'] += 1
                    print(f"   ✅ Cleaned source: {source.source_name}")
            
            session.commit()
            print(f"   📊 Cleaned {self.cleaning_stats['sources_cleaned']} sources")
            
        except Exception as e:
            session.rollback()
            print(f"   ❌ Error cleaning sources: {e}")
        finally:
            session.close()
    
    def strip_html(self, text: str) -> str:
        """Remove HTML tags from text"""
        if not text:
            return text
        
        # Remove HTML tags
        clean = re.compile('<.*?>')
        cleaned_text = re.sub(clean, '', text)
        
        # Clean up extra whitespace
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        
        return cleaned_text
    
    def extract_url_from_html(self, html_text: str) -> Optional[str]:
        """Extract URL from HTML text"""
        if not html_text:
            return None
        
        # Look for href attributes
        href_match = re.search(r'href=["\']([^"\']+)["\']', html_text)
        if href_match:
            return href_match.group(1)
        
        # Look for plain URLs
        url_match = re.search(r'https?://[^\s<>"\']+', html_text)
        if url_match:
            return url_match.group(0)
        
        return None
    
    def clean_email(self, email: str) -> str:
        """Clean email address"""
        if not email:
            return email
        
        # Remove HTML tags
        email = self.strip_html(email)
        
        # Extract email from text
        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', email)
        if email_match:
            return email_match.group(0)
        
        return email
    
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
    
    def print_cleaning_summary(self):
        """Print cleaning summary"""
        print(f"\n📊 Cleaning Summary")
        print("=" * 60)
        
        total_cleaned = sum(self.cleaning_stats.values())
        
        if total_cleaned > 0:
            print(f"✅ Cleaning completed successfully!")
            print(f"   Projects cleaned: {self.cleaning_stats['projects_cleaned']}")
            print(f"   Units cleaned: {self.cleaning_stats['units_cleaned']}")
            print(f"   Amenities removed: {self.cleaning_stats['amenities_removed']}")
            print(f"   Media links cleaned: {self.cleaning_stats['media_links_cleaned']}")
            print(f"   Sources cleaned: {self.cleaning_stats['sources_cleaned']}")
            print(f"   Total operations: {total_cleaned}")
        else:
            print("✅ No cleaning needed - data is already clean!")
        
        print(f"\n💡 Next Steps:")
        print("   1. Run validation again to verify fixes")
        print("   2. Export cleaned data to CSV")
        print("   3. Continue with spider runs")

def main():
    """Run data cleaning"""
    cleaner = DataCleaner()
    cleaner.clean_all_data()

if __name__ == '__main__':
    main()
