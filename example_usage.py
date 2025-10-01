#!/usr/bin/env python3
"""
Example usage of the luxury development scraper
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scraper.db.io import DatabaseManager
from scraper.pipelines.clean_normalize import CleanNormalizePipeline
from scraper.schemas import ProjectIn, UnitIn

def example_data_cleaning():
    """Example of data cleaning pipeline"""
    print("🧹 Example: Data Cleaning Pipeline")
    print("-" * 40)
    
    pipeline = CleanNormalizePipeline()
    
    # Example project data
    project_data = {
        'name': '  Luxury Tower  ',
        'developer_name': 'ABC Developers',
        'city': 'New York',
        'country': 'United States',
        'status': 'pre-construction',
        'address': '123 main street, new york, ny'
    }
    
    print("Original project data:")
    for key, value in project_data.items():
        print(f"  {key}: {value}")
    
    # Clean the data
    cleaned_data = pipeline._clean_project(project_data)
    
    print("\nCleaned project data:")
    for key, value in cleaned_data.items():
        print(f"  {key}: {value}")
    
    print()

def example_price_parsing():
    """Example of price parsing"""
    print("💰 Example: Price Parsing")
    print("-" * 40)
    
    pipeline = CleanNormalizePipeline()
    
    price_examples = [
        "$1,200,000",
        "£500,000",
        "AED 2,500,000",
        "From $1,000,000",
        "Price on request"
    ]
    
    for price_text in price_examples:
        price_data = pipeline._parse_price(price_text)
        if price_data:
            print(f"'{price_text}' -> {price_data}")
        else:
            print(f"'{price_text}' -> Could not parse")
    
    print()

def example_size_parsing():
    """Example of size parsing"""
    print("📏 Example: Size Parsing")
    print("-" * 40)
    
    pipeline = CleanNormalizePipeline()
    
    size_examples = [
        "1,200 sq ft",
        "120 m²",
        "2,500.5",
        "3,000 square feet"
    ]
    
    for size_text in size_examples:
        size_value = pipeline._parse_size(size_text)
        print(f"'{size_text}' -> {size_value}")
    
    print()

def example_database_operations():
    """Example of database operations"""
    print("🗄️ Example: Database Operations")
    print("-" * 40)
    
    # Create in-memory database for demo
    db = DatabaseManager("sqlite:///:memory:")
    db.init_database()
    
    # Example project data
    project_data = {
        'name': 'Luxury Tower',
        'developer_name': 'ABC Developers',
        'city': 'New York',
        'country': 'United States',
        'property_type': 'Residential',
        'status': 'planned',
        'description': 'A luxury residential tower in the heart of Manhattan'
    }
    
    # Insert project
    project = db.upsert_project(project_data)
    print(f"Created project: {project.name} (ID: {project.id})")
    
    # Add units
    units_data = [
        {
            'unit_name': 'Residence 01A',
            'bedrooms': 2.0,
            'bathrooms': 2.5,
            'size_sqft': 1200.0,
            'price_local_value': 1200000.0,
            'price_local_currency': 'USD',
            'price_note': 'From'
        },
        {
            'unit_name': 'Residence 02B',
            'bedrooms': 3.0,
            'bathrooms': 3.0,
            'size_sqft': 1800.0,
            'price_local_value': 1800000.0,
            'price_local_currency': 'USD',
            'price_note': 'From'
        }
    ]
    
    db.add_units(project.id, units_data)
    print(f"Added {len(units_data)} units")
    
    # Add amenities
    amenities = [
        'Swimming Pool',
        'Gym',
        'Concierge Service',
        'Rooftop Deck',
        'Parking'
    ]
    
    db.add_amenities(project.id, amenities)
    print(f"Added {len(amenities)} amenities")
    
    # Get statistics
    stats = db.get_stats()
    print(f"\nDatabase statistics:")
    for table, count in stats.items():
        print(f"  {table}: {count}")
    
    print()

def example_pydantic_validation():
    """Example of Pydantic validation"""
    print("✅ Example: Pydantic Validation")
    print("-" * 40)
    
    # Valid project data
    try:
        project = ProjectIn(
            name="Luxury Tower",
            developer_name="ABC Developers",
            city="New York",
            country="United States",
            contact_email="contact@example.com"
        )
        print(f"✓ Valid project: {project.name}")
    except Exception as e:
        print(f"✗ Validation failed: {e}")
    
    # Invalid project data (empty name)
    try:
        project = ProjectIn(
            name="",  # Empty name should fail
            developer_name="ABC Developers"
        )
        print(f"✗ Invalid project should have failed")
    except Exception as e:
        print(f"✓ Validation correctly rejected: {e}")
    
    # Valid unit data
    try:
        unit = UnitIn(
            unit_name="Residence 01A",
            bedrooms=2.0,
            bathrooms=2.5,
            size_sqft=1200.0,
            price_local_value=1200000.0,
            price_local_currency="USD"
        )
        print(f"✓ Valid unit: {unit.unit_name}")
    except Exception as e:
        print(f"✗ Validation failed: {e}")
    
    print()

def main():
    """Run all examples"""
    print("🏢 Luxury Development Scraper - Usage Examples")
    print("=" * 60)
    print()
    
    examples = [
        example_data_cleaning,
        example_price_parsing,
        example_size_parsing,
        example_database_operations,
        example_pydantic_validation
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"❌ Example failed: {e}")
            print()
    
    print("=" * 60)
    print("🎉 Examples completed!")
    print("\nTo run the actual scraper:")
    print("1. python -m scraper.cli init-db")
    print("2. python -m scraper.cli crawl --spider selene_fort_lauderdale")
    print("3. python -m scraper.cli export --table projects --output data/exports/projects.csv")

if __name__ == '__main__':
    main()
