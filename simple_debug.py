#!/usr/bin/env python3
"""
Simple debug script to test spider parsing
"""
import sys
from pathlib import Path
import requests
from bs4 import BeautifulSoup

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def debug_propertyguru():
    """Debug PropertyGuru website"""
    print("🔍 DEBUG: PropertyGuru Singapore")
    print("=" * 50)
    
    url = "https://www.propertyguru.com.sg/new-project-launch"
    
    try:
        # Make request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print(f"📡 Fetching: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Content Length: {len(response.text)}")
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check title
        title = soup.find('title')
        print(f"Page Title: {title.text if title else 'No title'}")
        
        # Look for listing containers
        listing_selectors = [
            '.listing-card',
            '.property-card', 
            '.project-card',
            '.search-result',
            '.listing',
            '.property',
            '.project',
            '[data-testid*="listing"]',
            '[class*="listing"]',
            '[class*="property"]',
            '[class*="project"]'
        ]
        
        print(f"\n🔍 Looking for listing containers:")
        for selector in listing_selectors:
            elements = soup.select(selector)
            count = len(elements)
            print(f"  {selector}: {count} elements")
            
            if count > 0:
                # Show first element
                first_element = elements[0]
                print(f"    First element: {str(first_element)[:200]}...")
        
        # Look for project links
        project_links = soup.find_all('a', href=lambda x: x and '/new-project/' in x)
        print(f"\n🔍 Project links found: {len(project_links)}")
        for i, link in enumerate(project_links[:5]):
            print(f"  {i+1}: {link.get('href')}")
        
        # Look for any links with "project" in them
        all_links = soup.find_all('a', href=True)
        project_related_links = [link.get('href') for link in all_links if 'project' in link.get('href', '').lower()]
        print(f"\n🔍 All project-related links: {len(project_related_links)}")
        for i, link in enumerate(project_related_links[:10]):
            print(f"  {i+1}: {link}")
        
        # Check for JavaScript content
        scripts = soup.find_all('script')
        print(f"\n🔍 JavaScript scripts found: {len(scripts)}")
        
        # Look for common patterns
        print(f"\n🔍 Common patterns:")
        if 'loading' in response.text.lower():
            print("  - Loading indicators found (may need JS)")
        if 'react' in response.text.lower():
            print("  - React framework detected")
        if 'vue' in response.text.lower():
            print("  - Vue framework detected")
        if 'angular' in response.text.lower():
            print("  - Angular framework detected")
        
        # Save HTML sample
        with open('debug_propertyguru.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"\n💾 HTML saved to: debug_propertyguru.html")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def debug_selene():
    """Debug Selene website (working spider)"""
    print("\n🔍 DEBUG: Selene Fort Lauderdale (Working)")
    print("=" * 50)
    
    url = "https://selenefortlauderdale.com/"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print(f"📡 Fetching: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Content Length: {len(response.text)}")
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check title
        title = soup.find('title')
        print(f"Page Title: {title.text if title else 'No title'}")
        
        # Look for project elements
        h1 = soup.find('h1')
        print(f"H1: {h1.text if h1 else 'No H1'}")
        
        # Look for amenities
        amenities = soup.find_all(['li', 'div'], string=lambda x: x and any(word in x.lower() for word in ['pool', 'gym', 'concierge', 'parking']))
        print(f"Amenities found: {len(amenities)}")
        for amenity in amenities[:5]:
            print(f"  - {amenity.get_text().strip()}")
        
        # Look for media links
        media_links = soup.find_all('a', href=lambda x: x and any(word in x.lower() for word in ['virtual', 'tour', 'brochure', '.pdf']))
        print(f"Media links found: {len(media_links)}")
        for link in media_links[:5]:
            print(f"  - {link.get('href')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Run debug tests"""
    print("🔍 SPIDER DEBUG ANALYSIS")
    print("=" * 60)
    
    # Debug working spider
    debug_selene()
    
    # Debug non-working spider
    debug_propertyguru()
    
    print(f"\n💡 Analysis complete!")

if __name__ == '__main__':
    main()
